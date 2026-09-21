from enum import Enum


class PipelineStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class WriteMode(str, Enum):
    APPEND = "append"
    OVERWRITE = "overwrite"
