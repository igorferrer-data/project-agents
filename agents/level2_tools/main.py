import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from agents.level2_tools.tool_agent import ToolAgent

def main():
    name = "Astra-Tool"
    persona = (
        "Você é Astra-Tool, a versão evoluída da Astra. "
        "Além de ser especialista em IA, você agora tem a capacidade de interagir com o sistema de arquivos local. "
        "Seja precisa, eficiente e sempre explique o que está fazendo."
    )

    print(f"--- Iniciando Agente Nível 2: {name} ---")
    print("(Sistemas de arquivos integrados. Digite 'sair' ou 'quit' para encerrar)\n")

    agent = ToolAgent(name=name, persona=persona)

    while True:
        try:
            user_input = input("Você: ")
            if user_input.lower() in ["sair", "quit"]:
                print(f"{name}: Desligando sistemas. Até mais!")
                break

            # The response may include the internal "THOUGHT" and "ACTION" logs,
            # we'll let the user see them so they understand the agent's reasoning process.
            response = agent.chat(user_input)
            print(f"\n{name}: {response}\n")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
