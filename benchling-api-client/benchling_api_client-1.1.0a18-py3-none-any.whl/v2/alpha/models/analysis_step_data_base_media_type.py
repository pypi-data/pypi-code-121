from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AnalysisStepDataBaseMediaType(Enums.KnownString):
    TEXTCSV = "text/csv"
    APPLICATIONZIP = "application/zip"
    TEXTHTML = "text/html"
    IMAGEJPEG = "image/jpeg"
    IMAGEPNG = "image/png"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AnalysisStepDataBaseMediaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of AnalysisStepDataBaseMediaType must be a string (encountered: {val})")
        newcls = Enum("AnalysisStepDataBaseMediaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AnalysisStepDataBaseMediaType, getattr(newcls, "_UNKNOWN"))
