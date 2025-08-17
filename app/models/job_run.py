#app/models/job_run.py

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class JobType(str, enum.Enum):
    os = "os"
    katana = "katana"
    # yeni job tipleri eklersen migration'da CHECK'i güncelle


class RunStatus(str, enum.Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class JobRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_runs"

    job_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default=RunStatus.CREATED.value)

    input_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    task_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    idempotency_key: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)

    # İlişki: 1 JobRun -> N Result (pratikte çoğu kez 1)
    results: Mapped[list["Result"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        # DB tarafındaki CHECK ile uyumlu ifadeler (autogenerate ile zorunlu değil, niyet beyanı)
        CheckConstraint("job_type IN ('os','katana')", name="ck_job_runs_job_type"),
        CheckConstraint(
            "status IN ('CREATED','QUEUED','STARTED','SUCCEEDED','FAILED','TIMEOUT','CANCELLED')",
            name="ck_job_runs_status",
        ),
    )

    # Küçük yardımcılar (domain niyeti)
    def mark_started(self) -> None:
        self.status = RunStatus.STARTED.value
        self.started_at = func.now()  # server-side timestamp

    def finish_success(self) -> None:
        self.status = RunStatus.SUCCEEDED.value
        self.finished_at = func.now()

    def finish_failed(self, summary: str | None = None) -> None:
        self.status = RunStatus.FAILED.value
        self.error_summary = summary
        self.finished_at = func.now()

    def finish_timeout(self, summary: str | None = None) -> None:
        self.status = RunStatus.TIMEOUT.value
        self.error_summary = summary
        self.finished_at = func.now()
