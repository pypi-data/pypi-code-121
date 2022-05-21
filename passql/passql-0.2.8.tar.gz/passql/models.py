from passql.interfaces import *
from typing import Set, Optional
from asyncpg import Record
import inspect

__all__ = (
    'DbEntity',
    'register_entities',
)


class DbEntity:
    __rec: Optional[Record]
    __fields: Set[str]

    def __init__(self):
        self.__rec = None

    @classmethod
    def _register_as_serializable(cls):
        def add_property(name: str):
            def get_value(self):
                if name in self.__dict__:
                    return self.__dict__[name]
                if self.__rec is not None and \
                        name in cls.__fields and name in self.__rec:
                    return self.__rec[name]
                raise AttributeError(f"{cls.__name__}.{name} field is not set!")

            def set_value(self, value):
                self.__dict__[name] = value

            setattr(cls, name, property(get_value, set_value))

        cls.__fields = set()
        for field_name in cls.__annotations__:
            add_property(field_name)
            cls.__fields.add(field_name)

    @classmethod
    def from_record(cls, rec: IDbRecord):
        obj = cls()
        obj.__rec = rec
        return obj


def register_entities():
    stack = inspect.stack()

    for obj in stack[1][0].f_locals.values():
        if type(obj) is type:
            if DbEntity in obj.__bases__:
                # noinspection PyProtectedMember
                obj._register_as_serializable()
