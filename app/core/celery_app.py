import os

from celery import Celery

from app.core.config import settings


is_test = os.getenv("APP_ENV", "").lower() == "test"

celery_app = Celery(
    "teamhub",
    broker="memory://" if is_test else settings.REDIS_URL,
    backend="cache+memory://" if is_test else settings.REDIS_URL,
    include=["app.core.audit"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_always_eager=is_test,
    task_eager_propagates=is_test,
)