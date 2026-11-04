import json
from typing import List, Dict, Any
from config.settings import AUDIT_LOG_FILE
from utils.logger import log_audit_event

class AuditLoggingAgent:
    """
    Agent 8: Audit and Compliance Agent.
    Monitors execution compliance, ensures masking integrity, and logs audit events.
    """
    def __init__(self):
        self.name = "AuditLoggingAgent"

    def record_run(self, session_id: str, email_id: str, status: str, summary: Dict[str, Any]):
        log_audit_event(
            agent_name=self.name,
            step="SessionCompleted",
            details={
                "session_id": session_id,
                "email_id": email_id,
                "status": status,
                "summary": summary
            }
        )

    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        logs = []
        if not AUDIT_LOG_FILE.exists():
            return logs
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    if line.strip():
                        logs.append(json.loads(line.strip()))
        except Exception:
            pass
        return logs

