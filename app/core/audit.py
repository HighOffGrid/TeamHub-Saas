from pathlib import Path
from datetime import datetime, UTC
from app.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

LOG_DIR = Path("logs")
AUDIT_FILE = LOG_DIR / "audit.log"


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def write_audit_log(self, action: str, actor_id: str, target: str, metadata: str = ""):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(
                f"{datetime.now(UTC).isoformat()} | {action} | actor={actor_id} | target={target} | {metadata}\n"
            )
    except Exception as exc:
        raise self.retry(exc=exc)


def dispatch_audit_log(action: str, actor_id: str, target: str, metadata: str = ""):
    try:
        write_audit_log.delay(action, actor_id, target, metadata)
    except Exception:
        logger.exception("Falha ao enfileirar audit log")