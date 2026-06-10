import sys
import os

# Add project root to sys.path
PROJECT_ROOT = "/home/iferrer/project-agents"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agents.level3_reasoning.reasoning_agent import ReasoningAgent

def main():
    name = "Astra-SuperReasoning"
    persona = (
        "Você é Astra-SuperReasoning, o ápice do raciocínio agêntico. "
        "Você opera com precisão cirúrgica, utilizando planos dinâmicos, "
        "auto-crítica adversária e execução de código para resolver problemas complexos. "
        "Sua comunicação é estritamente via JSON para garantir robustez técnica."
    )

    print(f"--- Iniciando Agente Nível 3 SUPER: {name} ---")
    print("(Protocolo: JSON -> Plan Checklist -> Adversarial Review -> Python Sandbox)")
    print("(Digite 'sair' ou 'quit' para encerrar)\n")

    agent = ReasoningAgent(name=name, persona=persona)

    # The Ultimate Test: RAG Lite -> Python Execution -> Verification
    test_query = (
        "Indexe o projeto, encontre onde o ToolManager está definido, "
        "escreva um pequeno script python temporário que conte todos os arquivos "
        "no diretório /home/iferrer/project-agents, execute esse script e "
        "me informe a contagem total como seu VERDICT."
    )

    print(f"Executando Teste de Capacidades Complexas:\n{test_query}\n")

    test_done = False
    while True:
        try:
            if not test_done:
                print(f"Executando Teste de Capacidades Complexas:\n{test_query}\n")
                response = agent.chat(test_query)
                print(f"\n{name}: {response}\n")
                test_done = True
            else:
                user_input = input("Você: ")
                if user_input.lower() in ["sair", "quit"]:
                    print(f"{name}: Encerrando sistemas de super-raciocínio. Até mais!")
                    break
                response = agent.chat(user_input)
                print(f"\n{name}: {response}\n")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
