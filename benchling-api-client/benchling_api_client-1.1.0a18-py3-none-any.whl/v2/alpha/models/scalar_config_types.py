from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ScalarConfigTypes(Enums.KnownString):
    TEXT = "text"
    FLOAT = "float"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    SECURE_TEXT = "secure_text"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ScalarConfigTypes":
        if not isinstance(val, str):
            raise ValueError(f"Value of ScalarConfigTypes must be a string (encountered: {val})")
        newcls = Enum("ScalarConfigTypes", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ScalarConfigTypes, getattr(newcls, "_UNKNOWN"))
