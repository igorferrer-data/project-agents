import openai
import json
import os
import sys
import re
from typing import Dict, Any, List, Optional

# Add project root to sys.path for imports
PROJECT_ROOT = "/home/iferrer/project-agents"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agents.level2_tools.tool_agent import ToolAgent
from tools.manager import ToolManager
from core.config import get_model_config

class ReasoningAgent(ToolAgent):
    """
    Level 3 Super-Reasoning Agent.
    Implements a robust JSON-based ReAct loop with explicit stateful planning,
    adversarial self-critique via a Reviewer persona, and a dynamic plan checklist.
    """
    def __init__(self, name: str, persona: str):
        super().__init__(name, persona)
        # Stateful plan tracking
        self.plan_checklist: List[Dict[str, Any]] = []
        # Updated persona for the Super-Reasoning protocol
        self.persona = self._augment_persona_with_super_reasoning()

    def _augment_persona_with_super_reasoning(self) -> str:
        """
        Injects the JSON protocol, stateful planning rules, and few-shot recovery examples.
        """
        tools_desc = self.tool_manager.get_tool_definitions()
        tools_text = "\n".join([f"- {t['name']}: {t['description']}" for t in tools_desc])

        protocol = (
            "\n\n--- SUPER-REASONING JSON PROTOCOL ---\n"
            "You MUST respond exclusively using a JSON object. Do not include any text outside the JSON block.\n\n"
            "JSON Schema:\n"
            "{\n"
            "  \"thought\": \"Your internal monologue and reasoning.\",\n"
            "  \"plan_update\": {\n"
            "    \"current_step\": <int>,\n"
            "    \"checklist\": [\"Step 1 (done/pending)\", \"Step 2 (pending)\", ...]\n"
            "  },\n"
            "  \"action\": {\n"
            "    \"tool\": \"tool_name\",\n"
            "    \"args\": { \"arg_name\": \"value\" }\n"
            "  } or null,\n"
            "  \"critique\": \"Analyze the last TOOL_RESULT. Is it correct? Does it change the plan?\",\n"
            "  \"verdict\": \"The final answer if all steps are complete\" or null\n"
            "}\n\n"
            "RULES:\n"
            "1. START with a full PLAN in the checklist.\n"
            "2. Every turn must include a THOUGHT and a CRITIQUE of the previous result (if applicable).\n"
            "3. Update the checklist as you progress.\n"
            "4. Only provide a VERDICT when you have verified all steps of your plan.\n\n"
            "--- RECOVERY EXAMPLES ---\n"
            "Example 1: Tool Error\n"
            "Input: 'Find config' -> ACTION: read_file(path='config.txt') -> TOOL_RESULT: 'File not found'\n"
            "Response: {\n"
            "  \"thought\": \"The file config.txt doesn't exist. I should look for a similar name.\",\n"
            "  \"plan_update\": { \"current_step\": 1, \"checklist\": [\"- [x] Read config (FAILED)\", \"- [ ] Search for config pattern\"] },\n"
            "  \"action\": { \"tool\": \"grep_search\", \"args\": { \"pattern\": \"config\", \"path\": \".\" } },\n"
            "  \"critique\": \"The direct path failed; searching recursively is the logical pivot.\",\n"
            "  \"verdict\": null\n"
            "}\n\n"
            f"Available Tools:\n{tools_text}"
        )
        return self.persona + protocol

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Robustly extracts and parses JSON from the LLM's response,
        handling markdown code blocks.
        """
        try:
            # Remove markdown code blocks (```json ... ```)
            clean_text = re.sub(r"```json\s*|\s*```", "", text).strip()
            # Find the first '{' and last '}'
            start = clean_text.find('{')
            end = clean_text.rfind('}')
            if start == -1 or end == -1:
                return None

            json_str = clean_text[start:end+1]
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return None

    def _get_reviewer_feedback(self, agent_turn: Dict[str, Any], observation: str) -> str:
        """
        Implements the Adversarial Critique (Reviewer persona).
        This is a 'hidden' call that challenges the agent's current reasoning.
        """
        reviewer_persona = (
            "You are a skeptical AI Reviewer. Your job is to find flaws in the Agent's reasoning. "
            "Analyze the Agent's thought, the Tool Result, and the Agent's critique. "
            "Does the Agent believe a result is successful when it's actually ambiguous? "
            "Did the Agent ignore a crucial detail in the observation? "
            "Provide a concise, harsh critique or a confirmation if it's truly correct."
        )

        messages = [
            {"role": "system", "content": reviewer_persona},
            {"role": "user", "content": f"Agent Turn: {json.dumps(agent_turn, indent=2)}\n\nObservation: {observation}\n\nReview this logic."}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Reviewer Error: {e}"

    def chat(self, user_input: str) -> str:
        """
        Super-Reasoning Loop: Checklist -> JSON Response -> Tool Execution -> Adversarial Review -> Update.
        """
        messages = [{"role": "system", "content": self.persona}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_input})

        max_iterations = 15
        current_iteration = 0
        self.plan_checklist = []

        while current_iteration < max_iterations:
            try:
                # Inject current checklist into the prompt
                checklist_ctx = ""
                if self.plan_checklist:
                    checklist_ctx = f"\n\nCURRENT CHECKLIST STATUS:\n{json.dumps(self.plan_checklist, indent=2)}"

                messages.append({"role": "system", "content": checklist_ctx})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                content = response.choices[0].message.content
                if checklist_ctx:
                    messages.pop()

                # Parse JSON
                turn_data = self._parse_json_response(content)
                if not turn_data:
                    err = "Error: Response was not valid JSON. Please use the JSON schema."
                    messages.append({"role": "system", "content": err})
                    current_iteration += 1
                    continue

                # Persist agent's thought and actions to history
                self.history.append({"role": "assistant", "content": content})

                # 1. Termination: Check for Verdict
                if turn_data.get("verdict"):
                    verdict = turn_data["verdict"]
                    if current_iteration == 0:
                        self.history.insert(-1, {"role": "user", "content": user_input})
                    self._save_history()
                    return verdict

                # 2. Update stateful checklist
                plan_update = turn_data.get("plan_update")
                if plan_update and isinstance(plan_update, dict) and "checklist" in plan_update:
                    self.plan_checklist = plan_update["checklist"]

                # 3. Tool Execution
                action = turn_data.get("action")
                if action and isinstance(action, dict) and "tool" in action:
                    tool_name = action["tool"]
                    args = action.get("args", {})

                    observation = self.tool_manager.execute(tool_name, args)

                    # --- ADVERSARIAL REVIEW PHASE ---
                    # The agent provides a critique, then the Reviewer challenges it
                    agent_critique = turn_data.get("critique", "No critique provided.")
                    reviewer_feedback = self._get_reviewer_feedback(turn_data, observation)

                    # Combine observation and reviewer feedback for the next turn
                    obs_message = (
                        f"TOOL_RESULT: {observation}\n\n"
                        f"AGENT_CRITIQUE: {agent_critique}\n"
                        f"REVIEWER_FEEDBACK: {reviewer_feedback}\n\n"
                        "Now, refine your thought, update the checklist if needed, and decide the next ACTION or VERDICT."
                    )

                    messages.append({"role": "system", "content": obs_message})
                    self.history.append({"role": "system", "content": obs_message})

                    current_iteration += 1
                    continue

                # Handle turns where agent is just thinking/planning without action
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "system", "content": "Please provide a JSON response containing an ACTION or a VERDICT."})
                current_iteration += 1

            except Exception as e:
                return f"Erro no Super-Loop de raciocínio: {str(e)}"

        return "Erro: O agente atingiu o limite de iterações sem chegar a um VERDICT."
