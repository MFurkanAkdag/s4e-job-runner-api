#app/schemas/enums.py

import enum


class JobType(str, enum.Enum):
    os = "os"
    katana = "katana"


class RunStatus(str, enum.Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
