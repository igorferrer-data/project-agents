import openai
import json
import os
from core.config import get_model_config

class SimpleAgent:
    """
    Level 1 Agent: Simple Agent.
    This agent has a specific persona (system prompt) and can maintain a conversation.
    It uses the LiteLLM bridge to communicate with the local LLM and persists history to JSON.
    """
    def __init__(self, name: str, persona: str):
        self.name = name
        self.persona = persona

        # Set up persistence path
        self.history_dir = os.path.join(os.path.dirname(__file__), "history")
        os.makedirs(self.history_dir, exist_ok=True)
        self.history_file = os.path.join(self.history_dir, f"{self.name.lower().replace(' ', '_')}.json")

        self.history = self._load_history()

        # Configure OpenAI client to point to the LiteLLM bridge
        config = get_model_config()
        self.client = openai.OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )
        self.model = config["model"]

    def _load_history(self):
        """Loads conversation history from a JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar histórico: {e}")
        return []

    def _save_history(self):
        """Saves current conversation history to a JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    def chat(self, user_input: str) -> str:
        """
        Processes user input and returns the agent's response.
        """
        # Build messages list starting with the system persona
        messages = [{"role": "system", "content": self.persona}]

        # Add conversation history
        messages.extend(self.history)

        # Add the current user message
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            agent_response = response.choices[0].message.content

            # Update history to maintain context
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": agent_response})

            # Persist history after each interaction
            self._save_history()

            return agent_response
        except Exception as e:
            return f"Erro ao processar resposta: {str(e)}"

    def reset_memory(self):
        """Clears the conversation history and deletes the saved file."""
        self.history = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
