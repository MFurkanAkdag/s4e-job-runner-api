#app/schemas/result.py

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, conlist


class OSResultPayload(BaseModel):
    exit_code: int
    stdout_snippet: str
    stderr_snippet: str
    stdout_bytes: int
    stderr_bytes: int


class KatanaResultPayload(BaseModel):
    total_urls: int
    unique_urls: int
    sample_urls: conlist(str, max_length=20) = Field(default_factory=list)
    tool_version: str | None = None


class ResultBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    created_at: datetime


class ResultRead(ResultBrief):
    data: dict
