from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ButtonUiBlockType(Enums.KnownString):
    BUTTON = "BUTTON"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ButtonUiBlockType":
        if not isinstance(val, str):
            raise ValueError(f"Value of ButtonUiBlockType must be a string (encountered: {val})")
        newcls = Enum("ButtonUiBlockType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ButtonUiBlockType, getattr(newcls, "_UNKNOWN"))
