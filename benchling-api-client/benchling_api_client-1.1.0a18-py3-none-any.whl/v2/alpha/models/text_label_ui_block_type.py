from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class TextLabelUiBlockType(Enums.KnownString):
    LABEL = "LABEL"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "TextLabelUiBlockType":
        if not isinstance(val, str):
            raise ValueError(f"Value of TextLabelUiBlockType must be a string (encountered: {val})")
        newcls = Enum("TextLabelUiBlockType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(TextLabelUiBlockType, getattr(newcls, "_UNKNOWN"))
