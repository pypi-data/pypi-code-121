import typing as T
from pydantic import BaseModel
from edgedb_orm import is_unset


class BasePatch(BaseModel):
    def updated_fields(
        self, exclude: T.Set[str] = None, exclude_last_updated: bool = False
    ) -> T.Set[str]:
        if exclude is None:
            exclude = set()
        if exclude_last_updated:
            exclude.add("last_updated")
        return {
            field
            for field in self.__fields__
            if field not in exclude and not is_unset(getattr(self, field))
        }
