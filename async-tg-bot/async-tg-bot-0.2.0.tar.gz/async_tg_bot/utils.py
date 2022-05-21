from typing import TypeVar

from pydantic import BaseModel

T = TypeVar('T')


def clear_params(params: dict) -> dict:
    def clear_obj(obj):
        if isinstance(obj, BaseModel):
            return obj.dict(exclude_none=True)
        if isinstance(obj, list):
            return [clear_obj(i) for i in obj]
        if isinstance(obj, dict):
            return {k: clear_obj(v) for k, v in obj.items() if clear_obj(v) is not None}
        return obj

    return clear_obj(params)


def listify(obj: T) -> T | list[T]:
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    if isinstance(obj, tuple):
        return list(obj)

    return [obj]
