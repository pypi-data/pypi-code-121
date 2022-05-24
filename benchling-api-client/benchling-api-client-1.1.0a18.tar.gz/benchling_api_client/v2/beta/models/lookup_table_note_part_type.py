from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class LookupTableNotePartType(Enums.KnownString):
    LOOKUP_TABLE = "lookup_table"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "LookupTableNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of LookupTableNotePartType must be a string (encountered: {val})")
        newcls = Enum("LookupTableNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(LookupTableNotePartType, getattr(newcls, "_UNKNOWN"))
