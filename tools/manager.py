import os
import subprocess
from typing import Any, Dict, List, Callable

class ToolManager:
    """
    Manages the registration and execution of tools that AI Agents can use.
    Provides a unified interface for the agent to interact with the local system.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()

    def register_tool(self, name: str, func: Callable, description: str):
        """Registers a new tool with a description."""
        self.tools[name] = {
            "function": func,
            "description": description
        }

    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Executes a registered tool with the given arguments."""
        if tool_name not in self.tools:
            return f"Erro: Ferramenta '{tool_name}' não encontrada."

        tool = self.tools[tool_name]["function"]
        try:
            # Pass arguments as keyword arguments
            result = tool(**args)
            return str(result)
        except Exception as e:
            return f"Erro ao executar ferramenta '{tool_name}': {str(e)}"

    def get_tool_definitions(self) -> List[Dict[str, str]]:
        """Returns descriptions of all available tools for the agent's system prompt."""
        return [
            {"name": name, "description": info["description"]}
            for name, info in self.tools.items()
        ]

    def _register_default_tools(self):
        """Registers the initial set of system tools."""
        self.register_tool(
            "list_files",
            self._list_files,
            "Lists files and directories in a given path. Args: {path: str}"
        )
        self.register_tool(
            "read_file",
            self._read_file,
            "Reads the content of a file. Args: {path: str}"
        )
        self.register_tool(
            "write_file",
            self._write_file,
            "Writes content to a file. Warning: Overwrites existing content. Args: {path: str, content: str}"
        )
        self.register_tool(
            "grep_search",
            self._grep_search,
            "Searches for a pattern in a directory recursively. Args: {pattern: str, path: str}"
        )

    # Tool Implementations
    def _list_files(self, path: str) -> str:
        try:
            files = os.listdir(path)
            return "\n".join(files) if files else "Pasta vazia."
        except Exception as e:
            return f"Erro ao listar arquivos: {e}"

    def _read_file(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Erro ao ler arquivo: {e}"

    def _write_file(self, path: str, content: str) -> str:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Arquivo {path} escrito com sucesso."
        except Exception as e:
            return f"Erro ao escrever arquivo: {e}"

    def _grep_search(self, pattern: str, path: str) -> str:
        try:
            # Using grep via subprocess for efficiency as per AerynOs rules
            result = subprocess.run(
                ["grep", "-r", pattern, path],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.stdout if result.stdout else "Nenhuma correspondência encontrada."
        except Exception as e:
            return f"Erro ao executar grep: {e}"
