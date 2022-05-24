from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListFeaturesMatchType(Enums.KnownString):
    NUCLEOTIDE = "nucleotide"
    PROTEIN = "protein"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListFeaturesMatchType":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListFeaturesMatchType must be a string (encountered: {val})")
        newcls = Enum("ListFeaturesMatchType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListFeaturesMatchType, getattr(newcls, "_UNKNOWN"))
