#app/schemas/jobs.py

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, HttpUrl, constr, conlist

from .enums import JobType  # status alanını str bıraktığımız için RunStatus import etmedik


class OSJobRequest(BaseModel):
    # düzeltme: Field(. ...) -> Field(..., ...)
    cmd: conlist(str, min_length=1) = Field(..., description="Komut ve argümanlar")
    cwd: str | None = Field(None, description="Çalışma dizini (opsiyonel)")
    env: dict[str, str] | None = Field(None, description="Ortam değişkenleri")
    timeout_sec: int | None = Field(None, ge=1, description="İşlem için timeout (saniye)")


class KatanaJobRequest(BaseModel):
    # düzeltme: Field(. ...) -> Field(..., ...)
    url: HttpUrl = Field(..., description="Tarama yapılacak URL")
    depth: int | None = Field(None, ge=0, description="Tarama derinliği")
    args: dict[str, str] | None = Field(None, description="Katana argümanları")
    timeout_sec: int | None = Field(None, ge=1, description="Timeout (saniye)")


class JobAcceptedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: UUID
    job_type: JobType
    # Not: burada mevcut projede 'str' kullanılıyor; tipi değiştirmedik (iyileştirme yapmama talebin doğrultusunda).
    status: str
    submitted_at: datetime
    trace_id: str | None = None
