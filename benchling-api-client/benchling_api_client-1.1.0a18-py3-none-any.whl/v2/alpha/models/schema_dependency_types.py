from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SchemaDependencyTypes(Enums.KnownString):
    CONTAINER_SCHEMA = "container_schema"
    PLATE_SCHEMA = "plate_schema"
    LOCATION_SCHEMA = "location_schema"
    BOX_SCHEMA = "box_schema"
    RUN_SCHEMA = "run_schema"
    RESULT_SCHEMA = "result_schema"
    REQUEST_SCHEMA = "request_schema"
    ENTRY_SCHEMA = "entry_schema"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SchemaDependencyTypes":
        if not isinstance(val, str):
            raise ValueError(f"Value of SchemaDependencyTypes must be a string (encountered: {val})")
        newcls = Enum("SchemaDependencyTypes", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SchemaDependencyTypes, getattr(newcls, "_UNKNOWN"))
