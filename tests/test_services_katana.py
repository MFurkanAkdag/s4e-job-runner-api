# tests/test_services_katana.py

from __future__ import annotations

from app.models.job_run import JobRun, JobType, RunStatus
from app.services import job_katana as svc


def test_service_katana_success(db, monkeypatch):
    run = JobRun(
        job_type=JobType.katana.value,
        status=RunStatus.QUEUED.value,
        input_payload={"url": "https://example.com"},
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Katana binary ve versiyon stub'ları
    monkeypatch.setattr(svc, "_katana_exists", lambda: True)
    monkeypatch.setattr(svc, "_katana_version", lambda: "katana 1.0.0")

    # _run_capture_lines 2 değer döndürmeli: (lines, duration_ms)
    def fake_capture(cmd, timeout):
        lines = [
            "https://example.com/",
            "https://example.com/a",
            "https://example.com/a",  # dup
            "https://example.com/b",
            "not-a-url",
        ]
        return lines, 42.0

    monkeypatch.setattr(svc, "_run_capture_lines", fake_capture)

    svc.run_katana(str(run.id))

    db.refresh(run)
    assert run.status == RunStatus.SUCCEEDED.value
    # metrik yazılmış olmalı
    assert run.metrics and run.metrics.get("duration_ms") is not None
