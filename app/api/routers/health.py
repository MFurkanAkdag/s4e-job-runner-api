#app/api/routers/health.py

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_session)) -> dict:
    # Basit DB ping (Postgres için)
    db.execute(text("SELECT 1"))
    return {"status": "ready"}
