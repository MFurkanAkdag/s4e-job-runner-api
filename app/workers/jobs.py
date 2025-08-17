# app/workers/jobs.py

from __future__ import annotations

import time
from typing import Optional

from celery import Task

from app.core.celery_app import celery_app
from app.core.logging import logger
from app.db.session import session_scope
from app.models.job_run import JobRun
from app.services.job_os_command import run_os_command as svc_run_os_command
from app.services.job_katana import run_katana as svc_run_katana


def _set_task_id_if_missing(run_id: str, task_id: str) -> None:
    """JobRun.task_id yoksa bir defaya mahsus ata (idempotent)."""
    with session_scope() as db:
        run: Optional[JobRun] = db.get(JobRun, run_id)
        if not run:
            logger.warning("JobRun not found while setting task_id: %s", run_id)
            return
        if not run.task_id:
            run.task_id = task_id  # session_scope çıkışında commit olur


class BaseJobTask(Task):
    # Gelecekte retry kullanmak istersek (servisler exception fırlatmalı)
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    max_retries = 5

    def before_start(self, task_id, args, kwargs):
        # run_id kwargs ile gelir; API böyle kuyruğa gönderiyor
        run_id = kwargs.get("run_id")
        if run_id:
            _set_task_id_if_missing(run_id, task_id)
        return super().before_start(task_id, args, kwargs)


@celery_app.task(
    name="app.workers.jobs.run_os_command",
    bind=True,
    base=BaseJobTask,
    acks_late=True,
    ignore_result=True,  # Celery backend’e sonuç yazma
)
def run_os_command(self: BaseJobTask, *, run_id: str) -> str:
    """OS komutu çalıştıran task."""
    logger.info("[OS] task_id=%s run_id=%s started", self.request.id, run_id)
    t0 = time.perf_counter()
    try:
        svc_run_os_command(run_id)
        return "ok"
    finally:
        dt = (time.perf_counter() - t0) * 1000
        logger.info("[OS] task_id=%s run_id=%s finished in %.0fms", self.request.id, run_id, dt)


@celery_app.task(
    name="app.workers.jobs.run_katana",
    bind=True,
    base=BaseJobTask,
    acks_late=True,
    ignore_result=True,
)
def run_katana(self: BaseJobTask, *, run_id: str) -> str:
    """Katana taramasını yapan task."""
    logger.info("[KATANA] task_id=%s run_id=%s started", self.request.id, run_id)
    t0 = time.perf_counter()
    try:
        svc_run_katana(run_id)
        return "ok"
    finally:
        dt = (time.perf_counter() - t0) * 1000
        logger.info("[KATANA] task_id=%s run_id=%s finished in %.0fms", self.request.id, run_id, dt)
