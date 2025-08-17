# app/services/job_os_command.py

from __future__ import annotations

import os
import subprocess
import time

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.session import session_scope
from app.models.job_run import JobRun
from app.models.result import Result

# Güvenlik: izinli komutlar (env ile override edilebilir: ALLOWED_CMDS="ls,pwd,whoami,uname,cat,echo")
DEFAULT_ALLOWED_CMDS = {"ls", "pwd", "whoami", "uname", "cat", "echo"}
ALLOWED_CMDS = (
    set((os.getenv("ALLOWED_CMDS", "") or "").split(","))
    if os.getenv("ALLOWED_CMDS")
    else DEFAULT_ALLOWED_CMDS
)

# Çıktı sınırlamaları
STD_SNIPPET_MAX = int(os.getenv("OS_STD_SNIPPET_MAX", "4096"))  # bytes/snippet


def _ensure_safe_cwd(cwd: str | None) -> str | None:
    if not cwd:
        return None
    base = os.path.realpath(settings.work_dir)
    target = os.path.realpath(cwd)
    # hedef, base altında değilse reddet
    if not target.startswith(base + os.sep) and target != base:
        raise ValueError(f"cwd '{cwd}' is not under WORK_DIR '{settings.work_dir}'")
    return target


def _sanitize_cmd(cmd: list[str]) -> list[str]:
    if not cmd or not cmd[0]:
        raise ValueError("Command cannot be empty")
    prog = os.path.basename(cmd[0])
    if prog not in ALLOWED_CMDS:
        raise ValueError(f"Command '{prog}' is not allowed")
    # Argümanlar shell'siz çağrılacak; injection riski yok.
    return cmd


def _truncate(s: str, limit: int) -> str:
    if len(s.encode("utf-8")) <= limit:
        return s
    b = s.encode("utf-8")[:limit]  # byte bazlı kes
    return b.decode("utf-8", errors="ignore")  # çok baytlı kesikleri yumuşat


def _run_subprocess(cmd: list[str], cwd: str | None, timeout: int) -> tuple[int, str, str, float]:
    start = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        rc = -1
    dur_ms = (time.perf_counter() - start) * 1000.0
    return rc, (out or ""), (err or ""), dur_ms


def run_os_command(run_id: str) -> None:
    """
    Worker tarafından çağrılır: OS komutunu çalıştırır ve sonucu kaydeder.
    """
    with session_scope() as db:  # type: Session
        run: JobRun | None = db.get(JobRun, run_id)
        if not run:
            logger.error("JobRun not found: %s", run_id)
            return

        try:
            # STARTED
            run.mark_started()
            db.flush()

            payload = run.input_payload or {}
            raw_cmd = payload.get("cmd")
            if not isinstance(raw_cmd, list) or not raw_cmd:
                raise ValueError("payload.cmd must be a non-empty list")

            cmd = _sanitize_cmd([str(x) for x in raw_cmd])
            cwd = _ensure_safe_cwd(payload.get("cwd")) or settings.work_dir
            timeout = int(payload.get("timeout_sec") or settings.os_cmd_timeout)

            rc, stdout, stderr, dur_ms = _run_subprocess(cmd, cwd, timeout)

            # Result verisi
            stdout_bytes = len(stdout.encode("utf-8"))
            stderr_bytes = len(stderr.encode("utf-8"))
            data = {
                "exit_code": rc,
                "stdout_snippet": _truncate(stdout, STD_SNIPPET_MAX),
                "stderr_snippet": _truncate(stderr, STD_SNIPPET_MAX),
                "stdout_bytes": stdout_bytes,
                "stderr_bytes": stderr_bytes,
            }
            run.metrics = {"duration_ms": int(dur_ms), "exit_code": rc}

            # status mapping
            if rc == 0:
                run.finish_success()
            elif rc == -1:
                run.finish_timeout("process timeout")
            else:
                run.finish_failed((stderr or "process failed")[:512])

            db.add(Result(run_id=run.id, data=data))

        except Exception as ex:  # noqa: BLE001
            logger.exception("OS job failed for %s", run_id)
            # Persist failure safely even if yukarıda bir şey patladıysa
            try:
                run.finish_failed(str(ex)[:512])
                db.add(Result(run_id=run.id, data={"error": str(ex)[:2048]}))
            except Exception as inner:  # Son çare: logla
                logger.error("Failed to persist failure for %s: %s", run_id, inner)
