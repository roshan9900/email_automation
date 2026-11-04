import os
from pathlib import Path

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

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "hybrid")  # 'hybrid', 'groq', 'ollama', 'openai'
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama3-8b-8192")

# Confidence thresholds
MIN_INTENT_CONFIDENCE = 0.70
MIN_ENTITY_CONFIDENCE = 0.75

