from pathlib import Path
from datetime import datetime, UTC

LOG_DIR = Path("logs")
AUDIT_FILE = LOG_DIR / "audit.log"


def write_audit_log(action: str, actor_id: str, target: str, metadata: str = ""):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now(UTC).isoformat()} | {action} | actor={actor_id} | target={target} | {metadata}\n"
        )