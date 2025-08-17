from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.models.job_run import JobRun, JobType, RunStatus

def test_list_and_get_job_runs(client, db):
    # 2 kayıt oluştur
    now = datetime.now(timezone.utc)
    obj1 = JobRun(job_type=JobType.os.value, status=RunStatus.CREATED.value, requested_at=now, input_payload={})
    obj2 = JobRun(job_type=JobType.katana.value, status=RunStatus.SUCCEEDED.value, requested_at=now, input_payload={})
    db.add_all([obj1, obj2])
    db.commit()

    # Liste
    r = client.get("/job-runs?limit=10&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert data["pagination"]["total"] >= 2
    assert len(data["items"]) >= 2

    # Detay
    rid = data["items"][0]["id"]
    r2 = client.get(f"/job-runs/{rid}")
    assert r2.status_code == 200
    d = r2.json()
    assert "job_type" in d
    assert "status" in d
