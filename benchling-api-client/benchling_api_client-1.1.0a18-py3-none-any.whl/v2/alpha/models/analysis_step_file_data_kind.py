from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AnalysisStepFileDataKind(Enums.KnownString):
    FILE = "FILE"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AnalysisStepFileDataKind":
        if not isinstance(val, str):
            raise ValueError(f"Value of AnalysisStepFileDataKind must be a string (encountered: {val})")
        newcls = Enum("AnalysisStepFileDataKind", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AnalysisStepFileDataKind, getattr(newcls, "_UNKNOWN"))
