#app/schemas/common.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ErrorModel(BaseModel):
    # düzeltme: Field(. ...) -> Field(..., ...)
    code: str = Field(..., examples=["validation_error"])
    message: str
    details: dict[str, Any] | list[Any] | None = None


class Pagination(BaseModel):
    limit: int
    offset: int
    total: int


T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    data: T


# Custom config for all response models
class BaseResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseDBModel(BaseResponseModel):
    id: UUID
    created_at: datetime

