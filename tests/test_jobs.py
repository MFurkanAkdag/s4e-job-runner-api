from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.job_run import JobRun, JobType, RunStatus

def test_post_jobs_os_idempotent(client, db, monkeypatch):
    # Celery send_task'i stubla
    sent = {}
    def fake_send_task(name, kwargs=None, queue=None):
        sent["name"] = name
        sent["kwargs"] = kwargs
        sent["queue"] = queue
        return True

    from app.core import celery_app as cap
    monkeypatch.setattr(cap.celery_app, "send_task", fake_send_task)

    headers = {"Idempotency-Key": "idem-123"}
    payload = {"cmd": ["echo", "hello"]}

    r1 = client.post("/jobs/os", json=payload, headers=headers)
    assert r1.status_code == 202
    body1 = r1.json()
    assert body1["job_type"] == "os"
    run_id_1 = UUID(body1["run_id"])

    # aynı key ile tekrar
    r2 = client.post("/jobs/os", json=payload, headers=headers)
    assert r2.status_code == 202
    body2 = r2.json()
    assert UUID(body2["run_id"]) == run_id_1

    # DB kaydı oluşmalı ve QUEUED olmalı
    obj = db.execute(select(JobRun).where(JobRun.id == run_id_1)).scalar_one()
    assert obj.job_type == JobType.os.value
    assert obj.status == RunStatus.QUEUED.value

def test_post_jobs_katana_basic(client, db, monkeypatch):
    # Celery send_task'i stubla
    sent = {}
    def fake_send_task(name, kwargs=None, queue=None):
        sent["name"] = name
        sent["kwargs"] = kwargs
        sent["queue"] = queue
        return True

    from app.core import celery_app as cap
    monkeypatch.setattr(cap.celery_app, "send_task", fake_send_task)

    payload = {"url": "https://example.com"}

    r = client.post("/jobs/katana", json=payload)
    assert r.status_code == 202
    resp = r.json()
    assert resp["job_type"] == "katana"
    assert "run_id" in resp
