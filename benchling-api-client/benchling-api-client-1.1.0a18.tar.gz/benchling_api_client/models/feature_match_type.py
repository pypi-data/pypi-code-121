from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class FeatureMatchType(Enums.KnownString):
    NUCLEOTIDE = "nucleotide"
    PROTEIN = "protein"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "FeatureMatchType":
        if not isinstance(val, str):
            raise ValueError(f"Value of FeatureMatchType must be a string (encountered: {val})")
        newcls = Enum("FeatureMatchType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(FeatureMatchType, getattr(newcls, "_UNKNOWN"))
