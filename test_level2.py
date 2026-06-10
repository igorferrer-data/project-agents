import sys
import os

# Definir o root do projeto explicitamente
PROJECT_ROOT = "/home/iferrer/project-agents"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agents.level2_tools.tool_agent import ToolAgent

def main():
    name = "Astra-Tool"
    persona = (
        "Você é Astra-Tool, a versão evoluída da Astra. "
        "Além de ser especialista em IA, você agora tem a capacidade de interagir com o sistema de arquivos local. "
        "Seja precisa, eficiente e sempre explique o que está fazendo."
    )
    
    try:
        agent = ToolAgent(name=name, persona=persona)
        
        test_queries = [
            "Qual o seu nome e quem é você?",
            "Quais são as suas funções e o que você consegue fazer no sistema?",
            "Você consegue ler o conteúdo do arquivo README.md para mim?"
        ]
        
        for query in test_queries:
            print(f"User: {query}")
            response = agent.chat(query)
            print(f"Astra-Tool: {response}\n")
            print("-" * 40)
    except Exception as e:
        print(f"Erro durante a execução dos testes: {e}")

if __name__ == "__main__":
    main()
