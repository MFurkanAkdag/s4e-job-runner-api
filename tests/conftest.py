# tests/conftest.py

from __future__ import annotations

import os
import uuid
import contextlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from alembic import command
from alembic.config import Config as AlembicConfig

# Uygulama importları
from app.main import app as fastapi_app
from app.db.session import get_session as real_get_session   # <-- get_session override
from app.api.deps import require_api_key as real_require_api_key


# --- Zorunlu: DATABASE_URL bir Postgres URL'i olmalı ---
@pytest.fixture(scope="session")
def database_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        pytest.fail("Env DATABASE_URL is not set for tests (Postgres URL bekleniyor).")
    if "postgresql" not in url:
        pytest.fail("DATABASE_URL must be a PostgreSQL URL for these tests.")
    return url


@pytest.fixture(scope="session")
def engine(database_url: str):
    eng = create_engine(database_url, future=True)
    # hızlı connectivity test
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    return eng


@pytest.fixture(scope="session", autouse=True)
def run_migrations(engine):
    """Alembic upgrade head (test DB üzerinde)."""
    alembic_cfg = AlembicConfig("alembic.ini")
    # alembic.ini sqlalchemy.url boş ise env’den alır; yine de set edelim
    alembic_cfg.set_main_option("sqlalchemy.url", engine.url.render_as_string(hide_password=False))
    command.upgrade(alembic_cfg, "head")
    yield
    # istersen teardown’da downgrade yapabilirsin


@pytest.fixture(scope="function")
def db(engine):
    """Her test için taze Session ve otomatik rollback."""
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session: Session = TestingSessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


# --- FastAPI dependency override’ları ---
@pytest.fixture(scope="function")
def client(db: Session, monkeypatch: pytest.MonkeyPatch):
    # get_session dependency override
    def _db_override():
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise

    fastapi_app.dependency_overrides[real_get_session] = _db_override

    # API-Key kontrolünü devre dışı bırak (testlerde sade olsun)
    def _noop_api_key():
        return None
    fastapi_app.dependency_overrides[real_require_api_key] = _noop_api_key

    with TestClient(fastapi_app) as c:
        yield c

    fastapi_app.dependency_overrides.clear()
