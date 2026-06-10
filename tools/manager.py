import os
import subprocess
import tempfile
import re
import json
from typing import Any, Dict, List, Callable

class ToolManager:
    """
    Manages the registration and execution of tools that AI Agents can use.
    Provides a unified interface for the agent to interact with the local system.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.index_file = os.path.join(os.path.dirname(__file__), "../.code_index.json")
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
        self.register_tool(
            "python_executor",
            self._python_executor,
            "Executes Python code in a sandboxed temporary file. Use this for complex data processing or calculations. Args: {code: str}"
        )
        self.register_tool(
            "code_indexer",
            self._code_indexer,
            "Scans the project for class and function definitions and saves an index. Args: {path: str}"
        )
        self.register_tool(
            "index_search",
            self._index_search,
            "Searches the project index for relevant files based on keywords. Args: {query: str}"
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
            result = subprocess.run(
                ["grep", "-r", pattern, path],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.stdout if result.stdout else "Nenhuma correspondência encontrada."
        except Exception as e:
            return f"Erro ao executar grep: {e}"

    def _python_executor(self, code: str) -> str:
        """Executes Python code safely in a temporary file."""
        try:
            # Basic safety check for dangerous modules
            dangerous_modules = ['shutil', 'os.remove', 'os.rmdir', 'os.system', 'os.popen']
            for mod in dangerous_modules:
                if mod in code:
                    return f"Erro de Segurança: O módulo ou função '{mod}' é proibido no executor."

            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tf:
                tf.write(code)
                tf_path = tf.name

            # Run the script with a 10 second timeout
            result = subprocess.run(
                ["python3", tf_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )

            # Clean up temp file
            os.remove(tf_path)

            if result.returncode == 0:
                return result.stdout if result.stdout else "Código executado com sucesso (sem saída)."
            else:
                return f"Erro na execução do código:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Erro: O código excedeu o tempo limite de 10 segundos."
        except Exception as e:
            return f"Erro inesperado no executor: {e}"

    def _code_indexer(self, path: str) -> str:
        """Scans the project for definitions and saves an index."""
        try:
            index = {}
            # Regex to match 'class Name:' or 'def name('
            pattern = re.compile(r"^(?:class|def)\s+(\w+)")

            for root, dirs, files in os.walk(path):
                # Skip hidden directories like .git or .claude
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.readlines()
                                symbols = [match.group(1) for line in content if (match := pattern.match(line.strip()))]
                                if symbols:
                                    index[file_path] = symbols
                        except Exception:
                            continue

            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=4)

            return f"Indexação concluída. {len(index)} arquivos indexados em {self.index_file}."
        except Exception as e:
            return f"Erro ao indexar código: {e}"

    def _index_search(self, query: str) -> str:
        """Searches the saved index for keywords."""
        try:
            if not os.path.exists(self.index_file):
                return "Erro: O índice não existe. Execute 'code_indexer' primeiro."

            with open(self.index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)

            results = []
            query_words = query.lower().split()
            for file_path, symbols in index.items():
                # Check if any query word matches any symbol in the file
                if any(word in symbol.lower() for word in query_words for symbol in symbols):
                    results.append(file_path)

            if results:
                return "Arquivos relevantes encontrados:\n" + "\n".join(results)
            else:
                return "Nenhuma correspondência encontrada no índice."
        except Exception as e:
            return f"Erro ao buscar no índice: {e}"
