from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntitySchemaDependencyType(Enums.KnownString):
    ENTITY_SCHEMA = "entity_schema"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntitySchemaDependencyType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntitySchemaDependencyType must be a string (encountered: {val})")
        newcls = Enum("EntitySchemaDependencyType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntitySchemaDependencyType, getattr(newcls, "_UNKNOWN"))
