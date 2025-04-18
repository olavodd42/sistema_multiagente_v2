"""
Configuração inicial do módulo da aplicação.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do LLM padrão
DEFAULT_LLM = os.getenv("DEFAULT_LLM", "groq")

__version__ = "1.0.0"