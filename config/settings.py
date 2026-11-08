import os
from pathlib import Path

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_FILE = CONFIG_DIR / "mock_db.json"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG_FILE = LOGS_DIR / "audit.log"

# System settings
BANK_NAME = "HDFC Bank"
SUPPORT_EMAIL = "support@hdfcbank.com"
SUPPORT_PHONE = "1800-202-6161"

# Local LLM / Ollama Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # Default to local 'ollama'
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", os.getenv("LLM_MODEL", "llama3"))
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
DEFAULT_MODEL = OLLAMA_MODEL

# Optional Cloud Providers (Groq, OpenAI)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Confidence thresholds
MIN_INTENT_CONFIDENCE = 0.70
MIN_ENTITY_CONFIDENCE = 0.75
