import os
import json
import logging
from datetime import datetime
from pathlib import Path
from config.settings import AUDIT_LOG_FILE

# Set up standard logger
logger = logging.getLogger("EmailAutomationAudit")
logger.setLevel(logging.INFO)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(ch)

def log_audit_event(agent_name: str, step: str, details: dict, execution_time_ms: float = 0.0):
    """
    Appends a structured JSON audit event to logs/audit.log
    """
    event = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "step": step,
        "execution_time_ms": round(execution_time_ms, 2),
        "details": details
    }
    
    logger.info(f"[{agent_name}] {step} | Latency: {execution_time_ms:.1f}ms")
    
    try:
        AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write audit event to file: {e}")

