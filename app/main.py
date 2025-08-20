# app/main.py

from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import check_db_connection
from app.core.logging import logger

from app.api.routers import jobs, job_runs, results, health
from app.api.errors import install_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        check_db_connection()
        logger.info("DB connection OK on startup")
    except Exception as exc:
        # Uygulama ayakta kalır; /ready ile healthcheck'e bırakıyoruz
        logger.error("DB connection failed on startup: %s", exc)
    yield
    # Shutdown (gerekirse kaynak temizliği eklenebilir)


app = FastAPI(
    title="Job Runner API",
    version="0.1.0",
    description="RESTful API for running OS commands and Katana scans asynchronously",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # test için tümünü açtık
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
