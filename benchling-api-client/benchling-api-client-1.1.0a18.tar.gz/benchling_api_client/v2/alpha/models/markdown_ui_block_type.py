from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MarkdownUiBlockType(Enums.KnownString):
    MARKDOWN = "MARKDOWN"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MarkdownUiBlockType":
        if not isinstance(val, str):
            raise ValueError(f"Value of MarkdownUiBlockType must be a string (encountered: {val})")
        newcls = Enum("MarkdownUiBlockType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MarkdownUiBlockType, getattr(newcls, "_UNKNOWN"))
