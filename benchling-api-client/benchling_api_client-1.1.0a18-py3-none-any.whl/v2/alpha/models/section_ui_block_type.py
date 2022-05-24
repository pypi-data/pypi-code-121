from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SectionUiBlockType(Enums.KnownString):
    SECTION = "SECTION"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SectionUiBlockType":
        if not isinstance(val, str):
            raise ValueError(f"Value of SectionUiBlockType must be a string (encountered: {val})")
        newcls = Enum("SectionUiBlockType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SectionUiBlockType, getattr(newcls, "_UNKNOWN"))
