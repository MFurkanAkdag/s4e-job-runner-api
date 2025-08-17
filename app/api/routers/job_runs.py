#app/api/routers/job_runs.py

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime
from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session

from app.api.deps import require_api_key
from app.db.session import get_session
from app.api.pagination import build_pagination, paginate_query
from app.models.job_run import JobRun, JobType, RunStatus
from app.schemas.job_run import JobRunBrief, JobRunListResponse, JobRunRead

router = APIRouter(prefix="/job-runs", tags=["job-runs"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=JobRunListResponse)
def list_job_runs(
    job_type: JobType | None = Query(default=None),
    status_: RunStatus | None = Query(default=None, alias="status"),
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = Query(default=None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_session)
):
    stmt = select(JobRun)

    conds = []
    if job_type:
        conds.append(JobRun.job_type == job_type.value)
    if status_:
        conds.append(JobRun.status == status_.value)
    if from_:
        conds.append(JobRun.requested_at >= from_)
    if to:
        conds.append(JobRun.requested_at <= to)

    if conds:
        stmt = stmt.where(and_(*conds))

    stmt = stmt.order_by(JobRun.requested_at.desc())

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    items = db.execute(paginate_query(stmt, limit, offset)).scalars().all()

    return JobRunListResponse(
        items=[JobRunBrief.model_validate(i) for i in items],
        pagination=build_pagination(total=total, limit=limit, offset=offset),
    )


@router.get("/{run_id}", response_model=JobRunRead)
def get_job_run(run_id: UUID, db: Session = Depends(get_session)):
    obj = db.get(JobRun, run_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    return JobRunRead.model_validate(obj)
