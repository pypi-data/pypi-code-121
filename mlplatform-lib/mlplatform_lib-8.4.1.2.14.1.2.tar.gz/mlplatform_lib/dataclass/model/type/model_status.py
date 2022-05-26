from enum import Enum


class ModelStatus(str, Enum):
    RUNNING = "running"
    FAIL = "failed"
    SUCCESS = "success"
