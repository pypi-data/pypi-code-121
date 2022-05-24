from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListAssayResultsSort(Enums.KnownString):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListAssayResultsSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListAssayResultsSort must be a string (encountered: {val})")
        newcls = Enum("ListAssayResultsSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListAssayResultsSort, getattr(newcls, "_UNKNOWN"))
