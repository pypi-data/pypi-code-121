from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class TextInputUiBlockType(Enums.KnownString):
    TEXT_INPUT = "TEXT_INPUT"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "TextInputUiBlockType":
        if not isinstance(val, str):
            raise ValueError(f"Value of TextInputUiBlockType must be a string (encountered: {val})")
        newcls = Enum("TextInputUiBlockType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(TextInputUiBlockType, getattr(newcls, "_UNKNOWN"))
