#app/db/session.py

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Sağlam bağlantı havuzu ayarları
def _make_engine(url: str) -> Engine:
    if not url:
        raise RuntimeError("DATABASE_URL is not set.")
    return create_engine(
        url,
        pool_size=5,
        max_overflow=5,
        pool_pre_ping=True,  # ölü bağlantı tespiti
        future=True,
    )

engine: Engine = _make_engine(DATABASE_URL)

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

def check_db_connection() -> None:
    """DB’ye kısa bir ping at; hata varsa exception fırlat."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency olarak kullan:
        def endpoint(db: Session = Depends(get_session)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Worker tarafında context manager: with session_scope() as db: ..."""
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
