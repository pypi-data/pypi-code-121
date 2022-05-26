from __future__ import annotations

import datetime
from typing import List, NamedTuple
from typing import Type as TypingType

from sila2.framework.abc.data_type import DataType
from sila2.framework.data_types.any import Any as AnyDataType
from sila2.framework.data_types.any import SilaAnyType
from sila2.framework.data_types.binary import Binary
from sila2.framework.data_types.boolean import Boolean
from sila2.framework.data_types.constrained import Constrained
from sila2.framework.data_types.data_type_definition import DataTypeDefinition
from sila2.framework.data_types.date import Date, SilaDateType
from sila2.framework.data_types.integer import Integer
from sila2.framework.data_types.list import List as ListDataType
from sila2.framework.data_types.real import Real
from sila2.framework.data_types.string import String
from sila2.framework.data_types.structure import Structure
from sila2.framework.data_types.time import Time
from sila2.framework.data_types.timestamp import Timestamp


class Import(NamedTuple):
    origin: str
    target: str


class Type(NamedTuple):
    representation: str
    imports: List[Import]

    @classmethod
    def from_type(cls, type_: TypingType) -> Type:
        return cls(type_.__name__, [Import(type_.__module__, type_.__name__)] if type_.__module__ != "builtins" else [])

    @classmethod
    def from_data_type(cls, data_type: DataType):
        if isinstance(data_type, Integer):
            return cls.from_type(int)
        if isinstance(data_type, String):
            return cls.from_type(str)
        if isinstance(data_type, Boolean):
            return cls.from_type(bool)
        if isinstance(data_type, Binary):
            return cls.from_type(bytes)
        if isinstance(data_type, Real):
            return cls.from_type(float)
        if isinstance(data_type, Timestamp):
            return cls.from_type(datetime.datetime)
        if isinstance(data_type, Time):
            return cls.from_type(datetime.time)
        if isinstance(data_type, Date):
            return cls.from_type(SilaDateType)
        if isinstance(data_type, AnyDataType):
            return cls.from_type(SilaAnyType)
        if isinstance(data_type, Constrained):
            return cls.from_data_type(data_type.base_type)
        if isinstance(data_type, ListDataType):
            element_type = cls.from_data_type(data_type.element_type)
            list_type = cls("List", [Import("typing", "List")])
            return cls(f"List[{element_type.representation}]", list_type.imports + element_type.imports)
        if isinstance(data_type, DataTypeDefinition):
            return cls(data_type._identifier, [])
        if isinstance(data_type, Structure):
            return cls("Any", [Import("typing", "Any")])
        else:
            raise NotImplementedError(f"Generating data type {data_type} is not yet implemented")


class Field(NamedTuple):
    name: str
    type: Type
    docstring: str

    @property
    def imports(self) -> List[Import]:
        return self.type.imports
