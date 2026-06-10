import sys
import os

PROJECT_ROOT = "/home/iferrer/project-agents"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agents.level3_reasoning.reasoning_agent import ReasoningAgent

def main():
    name = "Astra-Reasoning"
    persona = (
        "Você é Astra-Reasoning, a versão mais avançada da Astra. "
        "Você não apenas utiliza ferramentas, mas planeja cada passo de sua execução, "
        "critica seus próprios resultados e só entrega a resposta final após a validação total. "
        "Seja metódica, analítica e transparente em seu processo de raciocínio."
    )
    
    agent = ReasoningAgent(name=name, persona=persona)
    
    # Complex query requiring planning and tool use
    query = "Busque por um arquivo que contenha 'config' no nome na raiz do projeto, leia seu conteúdo e, se ele referenciar 'localhost', resuma as configurações de conexão. Caso contrário, informe que o arquivo não é uma configuração local."
    
    print(f"Executing Level 3 Reasoning Test...\nQuery: {query}\n")
    response = agent.chat(query)
    print(f"\nFinal Verdict:\n{response}")

if __name__ == "__main__":
    main()
