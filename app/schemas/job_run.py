#app/schemas/jub_run.py

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .enums import JobType, RunStatus
from .common import Pagination


class JobRunCreate(BaseModel):
    job_type: JobType
    input_payload: dict | None = None


class JobRunBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_type: JobType
    status: RunStatus
    requested_at: datetime
    finished_at: Optional[datetime] = None


class JobRunRead(JobRunBrief):
    input_payload: dict | None = None
    started_at: Optional[datetime] = None
    task_id: Optional[str] = None
    trace_id: Optional[str] = None
    metrics: dict | None = None
    error_summary: Optional[str] = None


class JobRunListQuery(BaseModel):
    job_type: Optional[JobType] = None
    status: Optional[RunStatus] = None
    from_: Optional[datetime] = Field(None, alias="from")
    to: Optional[datetime] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class JobRunListResponse(BaseModel):
    items: list[JobRunBrief]
    pagination: Pagination

