#app/api/deps.py

from __future__ import annotations

from app.core.config import settings
from typing import Annotated, Optional


from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_session


def require_api_key(x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None) -> None:
    expected = (settings.api_key or "").strip()
    if not expected:
        return  # dev için kapalı
    if expected == "changeme":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid server API key")
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")


def read_idempotency_key(
    idem: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None
) -> Optional[str]:
    return idem


# Genel DB dependency
def db_session() -> Session:
    # get_session bir generator dependency; burada sadece alias’lıyoruz
    return next(get_session())



