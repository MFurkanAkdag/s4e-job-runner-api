from __future__ import annotations

from sqlalchemy import select

from app.models.job_run import JobRun, JobType, RunStatus
from app.models.result import Result

def test_results_empty_then_has_one(client, db):
    # Run oluştur
    run = JobRun(job_type=JobType.os.value, status=RunStatus.SUCCEEDED.value, input_payload={})
    db.add(run)
    db.commit()
    db.refresh(run)

    # Başta boş liste
    r0 = client.get(f"/results/{run.id}")
    assert r0.status_code == 200
    assert r0.json() == []

    # Result ekle
    db.add(Result(run_id=run.id, data={"exit_code": 0, "stdout_snippet": "", "stderr_snippet": "", "stdout_bytes": 0, "stderr_bytes": 0}))
    db.commit()

    r1 = client.get(f"/results/{run.id}")
    assert r1.status_code == 200
    assert len(r1.json()) == 1
