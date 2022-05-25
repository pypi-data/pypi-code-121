from typing import TypeVar, Generic
import json

T = TypeVar("T")


class Parameter(Generic[T]):

    def __init__(self,
                 name: str,
                 title: str = "",
                 description: str = "",
                 value: T = None,
                 optional: bool = False,
                 default: T = None):
        self.__name = name
        self.__title = title
        self.__description = description
        self.__value = value
        self.__optional = optional
        self.__default = default

    def set_name(self, name: str):
        self.__name = name

    def get_name(self) -> str:
        return self.__name

    def set_description(self, description: str = ""):
        self.__description = description

    def get_description(self) -> str:
        return self.__description

    def set_value(self, value: T):
        self.__value = value

    def get_value(self) -> T:
        return self.__value

    def set_optional(self, optional: bool):
        self.__optional = optional

    def get_optional(self):
        return self.__optional

    def serialize(self):
        pass

    def deserialize(self):
        pass


class StringParameter(Parameter[str]):

    pass


class FileInputParameter(StringParameter):

    pass


class FileOutputParameter(StringParameter):

    pass


class OuterFileInputParameter(StringParameter):

    pass


class OuterFileOutputParameter(StringParameter):

    pass


class IntParameter(Parameter[int]):

    pass


class FloatParameter(Parameter[float]):

    pass


class BooleanParameter(Parameter[bool]):

    pass


class ListParameter(Parameter[list]):

    pass


class JsonParameter(Parameter[dict]):

    pass


class TupleParameter(Parameter[tuple]):

    pass





