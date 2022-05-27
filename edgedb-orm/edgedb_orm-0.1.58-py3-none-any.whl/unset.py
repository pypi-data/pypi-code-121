from pydantic import BaseModel


class Unset(BaseModel):
    pass


def is_unset(val: Unset) -> bool:
    return isinstance(val, Unset)


class ComputedPropertyException(Exception):
    pass


class AppendixPropertyException(Exception):
    pass
