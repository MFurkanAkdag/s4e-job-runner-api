#app/services/job_katana.py

from __future__ import annotations

import os
import re
import subprocess
import time
from datetime import datetime, timezone

from app.core.config import settings
from app.core.logging import logger
from app.db.session import session_scope
from app.models.job_run import JobRun, RunStatus
from app.models.result import Result

URL_RE = re.compile(r"^https?://", re.IGNORECASE)
SAMPLE_MAX = int(os.getenv("KATANA_SAMPLE_MAX", "20"))


def _katana_exists() -> bool:
    return os.path.isfile(settings.katana_bin) and os.access(settings.katana_bin, os.X_OK)


def _katana_version() -> str | None:
    try:
        out = subprocess.check_output([settings.katana_bin, "-version"], text=True, stderr=subprocess.STDOUT, timeout=5)
        return out.strip()
    except Exception:
        return None


def _build_katana_cmd(url: str, depth: int | None, args: dict[str, str] | None) -> list[str]:
    cmd = [settings.katana_bin, "-u", url, "-silent"]
    if depth is not None:
        cmd += ["-d", str(depth)]
    # izinli anahtarları beyaz liste (örnek set)
    allowed = {"-d", "-depth", "-silent", "-jc", "-http-proxy", "-timeout"}
    for k, v in (args or {}).items():
        if k not in allowed:
            raise ValueError(f"katana arg not allowed: {k}")
        if v is None or v == "":
            cmd.append(k)
        else:
            cmd += [k, str(v)]
    return cmd


def _run_capture_lines(cmd: list[str], timeout: int) -> tuple[list[str], float]:
    """Komutu çalıştırır; stdout satırlarını ve süreyi (ms) döndürür.
       (Not: 2 değer döndürür; çağıran yerde de 2 değer beklenmelidir.)"""
    start = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()  # bufferları boşalt
        raise  # Timeout'u yukarı aynen aktar
    dur_ms = (time.perf_counter() - start) * 1000.0
    if rc != 0:
        raise RuntimeError(f"katana failed (rc={rc}): {(err or '').strip()[:256]}")
    lines = [ln.strip() for ln in (out or "").splitlines() if ln.strip()]
    return lines, dur_ms


def run_katana(run_id: str) -> None:
    """
    Worker tarafından çağrılır: Katana ile URL taraması yapar, sayıları kaydeder.
    """
    with session_scope() as db:
        run: JobRun | None = db.get(JobRun, run_id)
        if not run:
            logger.error("JobRun not found: %s", run_id)
            return

        # STARTED
        run.status = RunStatus.STARTED.value
        run.started_at = datetime.now(timezone.utc)
        db.flush()

        try:
            payload = run.input_payload or {}
            url = payload.get("url")
            if not isinstance(url, str) or not URL_RE.match(url):
                raise ValueError("payload.url must be a valid http/https URL")

            depth = payload.get("depth")
            if depth is not None:
                depth = int(depth)

            args = payload.get("args")
            if args is not None and not isinstance(args, dict):
                raise ValueError("payload.args must be an object (dict)")

            timeout = int(payload.get("timeout_sec") or settings.katana_timeout)

            if not _katana_exists():
                raise FileNotFoundError(f"katana not found at {settings.katana_bin}")

            cmd = _build_katana_cmd(url, depth, args)

            # DİKKAT: _run_capture_lines 2 değer döndürür → 2 değişkene aç
            lines, dur_ms = _run_capture_lines(cmd, timeout)
            urls = [ln for ln in lines if URL_RE.match(ln)]
            uniq = list(dict.fromkeys(urls))  # stable dedup
            sample = uniq[:SAMPLE_MAX]

            data = {
                "total_urls": len(urls),
                "unique_urls": len(uniq),
                "sample_urls": sample,
                "tool_version": _katana_version(),
            }

            run.metrics = {"duration_ms": int(dur_ms)}
            run.finished_at = datetime.now(timezone.utc)
            run.status = RunStatus.SUCCEEDED.value
            run.error_summary = None

            db.add(Result(run_id=run.id, data=data))

        except subprocess.TimeoutExpired:
            run.status = RunStatus.TIMEOUT.value
            run.finished_at = datetime.now(timezone.utc)
            run.error_summary = "katana timeout"
            db.add(Result(run_id=run.id, data={"error": "timeout"}))

        except Exception as ex:  # noqa: BLE001
            logger.exception("Katana job failed for %s", run_id)
            run.status = RunStatus.FAILED.value
            run.finished_at = datetime.now(timezone.utc)
            run.error_summary = str(ex)[:512]
            db.add(Result(run_id=run.id, data={"error": str(ex)[:2048]}))
