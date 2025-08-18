# app/api/routers/jobs.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import read_idempotency_key, require_api_key
from app.db.session import get_session
from app.models.job_run import JobRun, RunStatus, JobType
from app.schemas.jobs import JobAcceptedResponse, OSJobRequest, KatanaJobRequest
from app.core.celery_app import celery_app

router = APIRouter(prefix="/jobs", tags=["jobs"], dependencies=[Depends(require_api_key)])


def _find_idempotent_run(db: Session, idem_key: Optional[str]) -> Optional[JobRun]:
    if not idem_key:
        return None
    stmt = select(JobRun).where(JobRun.idempotency_key == idem_key)
    return db.execute(stmt).scalars().first()


@router.post("/os", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_os_job(
    body: OSJobRequest,
    db: Session = Depends(get_session),
    idem_key: Optional[str] = Depends(read_idempotency_key),
):
    # Idempotency: aynı key ile daha önce oluşturulmuş mu?
    existing = _find_idempotent_run(db, idem_key)
    if existing:
        return JobAcceptedResponse(
            run_id=existing.id,
            job_type=JobType.os,
            status=existing.status,
            submitted_at=existing.requested_at,
            trace_id=existing.trace_id,
        )

    run = JobRun(
        job_type=JobType.os.value,
        status=RunStatus.QUEUED.value,
        input_payload=body.model_dump(mode="json"),  # FIX
        idempotency_key=idem_key,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Kuyruğa gönder
    celery_app.send_task(
        "app.workers.jobs.run_os_command",
        kwargs={"run_id": str(run.id)},
        queue="os",
    )

    return JobAcceptedResponse(
        run_id=run.id,
        job_type=JobType.os,
        status=run.status,
        submitted_at=run.requested_at,
        trace_id=run.trace_id,
    )


@router.post("/katana", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_katana_job(
    body: KatanaJobRequest,
    db: Session = Depends(get_session),
    idem_key: Optional[str] = Depends(read_idempotency_key),
):
    existing = _find_idempotent_run(db, idem_key)
    if existing:
        return JobAcceptedResponse(
            run_id=existing.id,
            job_type=JobType.katana,
            status=existing.status,
            submitted_at=existing.requested_at,
            trace_id=existing.trace_id,
        )

    run = JobRun(
        job_type=JobType.katana.value,
        status=RunStatus.QUEUED.value,
        input_payload=body.model_dump(mode="json"),  # FIX
        idempotency_key=idem_key,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    celery_app.send_task(
        "app.workers.jobs.run_katana",
        kwargs={"run_id": str(run.id)},
        queue="katana",
    )

    return JobAcceptedResponse(
        run_id=run.id,
        job_type=JobType.katana,
        status=run.status,
        submitted_at=run.requested_at,
        trace_id=run.trace_id,
    )
