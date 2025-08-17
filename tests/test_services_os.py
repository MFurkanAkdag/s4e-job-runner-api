from __future__ import annotations

from app.models.job_run import JobRun, JobType, RunStatus
from app.services import job_os_command as svc


def test_service_os_success(db, monkeypatch):
    # Run kaydı
    run = JobRun(job_type=JobType.os.value, status=RunStatus.QUEUED.value, input_payload={"cmd": ["echo", "hi"]})
    db.add(run)
    db.commit()
    db.refresh(run)

    # Subprocess'i stubla
    def fake_run(cmd, cwd, timeout):
        return 0, "hello\n", "", 12.3
    monkeypatch.setattr(svc, "_run_subprocess", fake_run)

    svc.run_os_command(str(run.id))

    db.refresh(run)
    assert run.status == RunStatus.SUCCEEDED.value
    assert run.metrics.get("exit_code") == 0

def test_service_os_timeout(db, monkeypatch):
    run = JobRun(job_type=JobType.os.value, status=RunStatus.QUEUED.value, input_payload={"cmd": ["echo", "hi"], "timeout_sec": 1})
    db.add(run)
    db.commit()
    db.refresh(run)

    def fake_run(cmd, cwd, timeout):
        return -1, "", "", 1000.0
    monkeypatch.setattr(svc, "_run_subprocess", fake_run)

    svc.run_os_command(str(run.id))

    db.refresh(run)
    assert run.status == RunStatus.TIMEOUT.value
