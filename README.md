# 🤖 Agentes de IA: A Revolução do Trabalho

Bem-vindo ao projeto **Agentes de IA**. Este repositório é dedicado ao estudo, desenvolvimento e exploração de como Agentes de Inteligência Artificial podem ser criados e de que maneira eles estão transformando a natureza do trabalho contemporâneo.

## 📌 Visão Geral

A Inteligência Artificial evoluiu de simples modelos de chat (LLMs) para **Sistemas Agênticos**. Enquanto um chatbot responde a perguntas, um **Agente de IA** consegue:
- **Planejar**: Decompor tarefas complexas em sub-etapas.
- **Agir**: Utilizar ferramentas externas (APIs, Bash, Navegadores) para interagir com o mundo real.
- **Raciocinar**: Avaliar os resultados de suas ações e corrigir a rota se necessário.
- **Memória**: Manter contexto de longo e curto prazo para personalizar a execução.

## 🛠️ Arquitetura de Implementação

O projeto segue uma progressão de complexidade dividida em quatro níveis:

### 🟢 Level 1: Simple Agent (Implementado)
Focado em identidade e conversação básica.
- **Funcionalidade**: Agentes com persona definida via System Prompt.
- **Memória**: Implementação de persistência de histórico via JSON, permitindo que o agente lembre de conversas entre sessões.
- **Exemplo**: *Astra*, assistente de pesquisa em IA.

### 🟡 Level 2: Tool-Enabled Agent (Implementado)
Transição de "modelo de chat" para "modelo de ação".
- **ToolManager**: Sistema centralizado de registro e execução de ferramentas.
- **Capacidades**: Acesso ao sistema de arquivos (listar, ler, escrever e buscar arquivos via grep).
- **Loop de Raciocínio**: Implementação do ciclo `Pensamento $\rightarrow$ Ação $\rightarrow$ Observação`.
- **Exemplo**: *Astra-Tool*, capaz de interagir com o ambiente local para realizar tarefas técnicas.

### 🟠 Level 3: Reasoning Agent (Planejado)
Implementação de frameworks de raciocínio avançado como Chain-of-Thought (CoT) e ReAct para tarefas de alta complexidade.

### 🔴 Level 4: Multi-Agent Systems (Planejado)
Orquestração de múltiplos agentes especializados trabalhando em paralelo para resolver problemas complexos.

## 🚀 Fluxo de Trabalho e Memória

Para garantir a rastreabilidade e a eficiência do desenvolvimento no ambiente AerynOs:
- **`PROJECT_JOURNAL.md`**: Diário de bordo com registros de todas as decisões arquiteturais e marcos de implementação.
- **Persistência**: Todos os agentes possuem memória local persistente em JSON.
- **Eficiência**: O projeto prioriza operações de sistema eficientes (`grep`, `sed`, `ls -R`).

## 🎯 Objetivos do Projeto
- Explorar frameworks de criação de agentes.
- Implementar protótipos de agentes especializados para tarefas de engenharia.
- Documentar a curva de aprendizado e os gargalos de implementação de agentes locais.

---
*Desenvolvido no ambiente AerynOs com o apoio da Laura (AI Agent).*
