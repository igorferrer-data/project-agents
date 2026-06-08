# core/config.py
# Centralização de configurações para os Agentes de IA

import os

# Configurações do Modelo (Ollama / Local)
MODEL_NAME = "gemma4:31b-cloud"
BASE_URL = "http://localhost:4000" # Default LiteLLM bridge
API_KEY = "sk-local"

# Configurações de Sistema
PROJECT_ROOT = "/home/iferrer/project-agents/"
LOG_LEVEL = "INFO"

def get_model_config():
    """Retorna as configurações atuais do modelo."""
    return {
        "model": MODEL_NAME,
        "base_url": BASE_URL,
        "api_key": API_KEY
    }
