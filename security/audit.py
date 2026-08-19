import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("security.audit")

class AuditLogger:
    def __init__(self, log_dir="data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit.log"

    def log_action(self, user, mode, command, risk_status, approved, result=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "mode": mode,
            "command": command,
            "risk_status": risk_status,
            "approved": approved,
            "result": result[:200] if result and isinstance(result, str) else str(result)
        }
        
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            logger.info(f"Audit log entry added: {command} ({risk_status})")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
        
        return entry
