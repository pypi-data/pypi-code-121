from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class FeatureCreateMatchType(Enums.KnownString):
    NUCLEOTIDE = "nucleotide"
    PROTEIN = "protein"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "FeatureCreateMatchType":
        if not isinstance(val, str):
            raise ValueError(f"Value of FeatureCreateMatchType must be a string (encountered: {val})")
        newcls = Enum("FeatureCreateMatchType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(FeatureCreateMatchType, getattr(newcls, "_UNKNOWN"))
