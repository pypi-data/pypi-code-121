from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListRNASequencesSort(Enums.KnownString):
    MODIFIEDAT = "modifiedAt"
    MODIFIEDATASC = "modifiedAt:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAME = "name"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListRNASequencesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListRNASequencesSort must be a string (encountered: {val})")
        newcls = Enum("ListRNASequencesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListRNASequencesSort, getattr(newcls, "_UNKNOWN"))
