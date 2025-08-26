# app/main.py
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import check_db_connection
from app.core.logging import logger

from app.api.routers import jobs, job_runs, results, health
from app.api.errors import install_exception_handlers


def _parse_cors_origins() -> list[str]:
    """
    CORS_ORIGINS env'inden virgül ayrılmış origin listesi okur.
     """
    raw = (os.getenv("CORS_ORIGINS") or "").strip()
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        check_db_connection()
        logger.info("DB connection OK on startup")
    except Exception as exc:
        # Uygulama ayakta kalsın; /ready ile healthcheck'e bırakıyoruz
        logger.error("DB connection failed on startup: %s", exc)
    yield
    # Shutdown (gerekirse kaynak temizliği eklenebilir)


app = FastAPI(
    title="Job Runner API",
    version="0.1.0",
    description="RESTful API for running OS commands and Katana scans asynchronously",
    lifespan=lifespan,
)

# --- CORS ---
cors_origins = _parse_cors_origins()
# Eğer env verilmemişse dev için yalnızca lokal portları açalım
default_dev_origins = ["http://localhost:5173", "http://localhost:5174"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or default_dev_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Idempotency-Key"],
)

# Exception handler’ları yükle
install_exception_handlers(app)

# Router’ları ekle
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(job_runs.router)
app.include_router(results.router)


@app.get("/")
def root():
    return {"service": "job-runner-api"}
