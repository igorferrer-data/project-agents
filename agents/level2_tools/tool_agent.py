import openai
import json
import os
import sys

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from agents.level1_simple.simple_agent import SimpleAgent
from tools.manager import ToolManager
from core.config import get_model_config

class ToolAgent(SimpleAgent):
    """
    Level 2 Agent: Tool-Enabled Agent.
    Extends SimpleAgent by adding a ToolManager and a reasoning loop
    that allows the agent to interact with the local system.
    """
    def __init__(self, name: str, persona: str):
        super().__init__(name, persona)
        self.tool_manager = ToolManager()
        # Update persona to include instructions on how to use tools
        self.persona = self._augment_persona_with_tools()

    def _augment_persona_with_tools(self) -> str:
        """Adds tool descriptions and usage format to the agent's persona."""
        tools_desc = self.tool_manager.get_tool_definitions()
        tools_text = "\n".join([f"- {t['name']}: {t['description']}" for t in tools_desc])

        augmentation = (
            "\n\n--- TOOL USE PROTOCOL ---\n"
            "You have access to the following tools:\n"
            f"{tools_text}\n\n"
            "When you need a tool, respond ONLY with the following format:\n"
            "THOUGHT: <your reasoning about why you need the tool>\n"
            "ACTION: tool_name(arg1=value1, arg2=value2)\n"
            "--- END ACTION ---\n\n"
            "After receiving the TOOL_RESULT, you must analyze it and provide the final answer to the user.\n"
            "If you have enough information, just respond normally without using tools."
        )
        return self.persona + augmentation

    def chat(self, user_input: str) -> str:
        """
        Processes user input using a reasoning loop: Thought -> Action -> Observation.
        """
        # Build messages list
        messages = [{"role": "system", "content": self.persona}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_input})

        max_iterations = 5
        current_iteration = 0

        while current_iteration < max_iterations:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                content = response.choices[0].message.content

                # Check if the agent wants to use a tool
                if "ACTION:" in content and "--- END ACTION ---" in content:
                    # Parse tool call
                    action_part = content.split("ACTION:")[1].split("--- END ACTION ---")[0].strip()
                    # Simple parser for tool_name(arg1=val1, ...)
                    tool_name, args_str = action_part.split("(", 1)
                    args_str = args_str.rstrip(")")

                    # Parse arguments: "path='/home/user', content='hi'" -> {'path': '/home/user', 'content': 'hi'}
                    args = {}
                    if args_str:
                        for pair in args_str.split(","):
                            k, v = pair.split("=", 1)
                            # Strip quotes from values
                            args[k.strip()] = v.strip().strip("'").strip('"')

                    # Execute the tool
                    observation = self.tool_manager.execute(tool_name, args)

                    # Append the action and observation to the conversation
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "system", "content": f"TOOL_RESULT: {observation}"})

                    current_iteration += 1
                    continue # Go back to the LLM to process the observation
                else:
                    # No tool needed, final answer reached
                    self.history.append({"role": "user", "content": user_input})
                    self.history.append({"role": "assistant", "content": content})
                    self._save_history()
                    return content

            except Exception as e:
                return f"Erro no loop de raciocínio: {str(e)}"

        return "Erro: O agente atingiu o limite máximo de iterações de ferramentas sem chegar a uma resposta final."
