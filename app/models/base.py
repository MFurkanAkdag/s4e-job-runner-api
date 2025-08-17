#app/models/base.py


from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 Declarative Base"""


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),  # requires pgcrypto
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def touch(self) -> None:
        # Uygulama tarafında da dokunmak istersen
        self.updated_at = datetime.now(timezone.utc)  # noqa: SLF001


class ToDictMixin:
    def as_dict(self) -> Dict[str, Any]:
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}  # type: ignore[attr-defined]
