# app/core/config.py
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env desteği + env adları birebir alanlara bağlanır
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # Tanımsız env değişkenlerini yok say
        case_sensitive=False,    # DATABASE_URL / database_url ikisini de yakala
    )

    # DB ve Broker
    database_url: str = Field("", env="DATABASE_URL")
    broker_url: str = Field("amqp://guest:guest@rabbitmq:5672//", env="CELERY_BROKER_URL")
    result_backend: str = Field("rpc://", env="CELERY_RESULT_BACKEND")

    # Çalışma alanı ve araç yolları
    work_dir: str = Field("/workspace/jobs", env="WORK_DIR")
    katana_bin: str = Field("/usr/local/bin/katana", env="KATANA_BIN")

    # Timeout değerleri (saniye)
    os_cmd_timeout: int = Field(300, env="OS_CMD_TIMEOUT_SEC")
    katana_timeout: int = Field(300, env="KATANA_TIMEOUT_SEC")

    # Log
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # API güvenliği
    api_key: str = Field("changeme", env="API_KEY")


settings = Settings()
