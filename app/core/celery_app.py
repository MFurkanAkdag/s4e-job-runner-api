# app/core/celery_app.py
from celery import Celery
from app.core.config import settings
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "jobrunner",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["app.workers.jobs"],   # <-- EKLE
)

_default_soft = max(int(settings.os_cmd_timeout), int(settings.katana_timeout))
_default_hard = _default_soft + 30

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=_default_hard,
    task_soft_time_limit=_default_soft,
    result_expires=3600,
    task_default_queue="default",
    enable_utc=True,
    timezone="UTC",
)

celery_app.conf.task_routes = {
    "app.workers.jobs.run_os_command": {"queue": "os"},
    "app.workers.jobs.run_katana": {"queue": "katana"},
}
