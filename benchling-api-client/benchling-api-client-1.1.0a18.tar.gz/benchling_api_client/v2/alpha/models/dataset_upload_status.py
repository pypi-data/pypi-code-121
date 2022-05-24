from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DatasetUploadStatus(Enums.KnownString):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED_VALIDATION = "FAILED_VALIDATION"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DatasetUploadStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of DatasetUploadStatus must be a string (encountered: {val})")
        newcls = Enum("DatasetUploadStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DatasetUploadStatus, getattr(newcls, "_UNKNOWN"))
