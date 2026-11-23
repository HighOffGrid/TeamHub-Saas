FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /app/logs

CMD ["celery", "-A", "app.core.celery_app:celery_app", "worker", "--loglevel=info"]