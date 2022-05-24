from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AnalysisStepStatus(Enums.KnownString):
    BLOCKED = "BLOCKED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AnalysisStepStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of AnalysisStepStatus must be a string (encountered: {val})")
        newcls = Enum("AnalysisStepStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AnalysisStepStatus, getattr(newcls, "_UNKNOWN"))
