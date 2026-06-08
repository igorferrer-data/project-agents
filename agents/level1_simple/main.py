import sys
import os

# Add the project root to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from agents.level1_simple.simple_agent import SimpleAgent

def main():
    # Define a persona for our level 1 agent
    name = "Astra"
    persona = (
        "Você é Astra, uma assistente de pesquisa especializada em Inteligência Artificial. "
        "Seu tom é profissional, porém curioso e encorajador. "
        "Você busca sempre conectar conceitos técnicos com aplicações práticas."
    )

    print(f"--- Iniciando Agente Nível 1: {name} ---")
    print("(Digite 'sair' ou 'quit' para encerrar a conversa)\n")

    agent = SimpleAgent(name=name, persona=persona)

    while True:
        try:
            user_input = input("Você: ")
            if user_input.lower() in ["sair", "quit"]:
                print(f"{name}: Tchau! Até a próxima.")
                break

            response = agent.chat(user_input)
            print(f"\n{name}: {response}\n")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
