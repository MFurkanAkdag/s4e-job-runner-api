#app/core/logging.py

from __future__ import annotations

import logging
import sys

from app.core.config import settings

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("jobrunner")
