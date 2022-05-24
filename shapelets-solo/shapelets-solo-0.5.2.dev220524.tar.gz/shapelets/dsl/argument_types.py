# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from __future__ import annotations
import base64
import copy
import cloudpickle
from enum import Enum
import numpy as np
import pickle
import typing

from shapelets.dsl.exceptions import TypeNotSupported
from shapelets.model import (
    Capsule,
    Dataframe,
    Image,
    InvalidArgumentValue,
    Match,
    Model,
    NDArray,
    Sequence,
    View,
    ViewGroupEntry
)

# <T>: Generic attribute type, represents Shapelets' supported types.
#      (DSL functions support in addition Node and InputParameter)

SupportedTypes = typing.TypeVar(
    'T',
    bool,
    Capsule,
    Dataframe,
    float,
    int,
    Match,
    Model,
    NDArray,
    np.ndarray,
    Sequence,
    str,
    typing.Callable,
    typing.List,
    View,
    ViewGroupEntry)


class AttributeNames(Enum):
    ARRAY = "array"
    BOOL = "bool"
    BYTE = "byte"
    CAPSULE = "capsule"
    DATAFRAME = "dataframe"
    DOUBLE = "double"
    FLOAT = "float"
    FUNCTION = "function"
    IMAGE = "image"
    INT = "int"
    LIST = "list"
    LONG = "long"
    MATCH = "match"
    MODEL = "model"
    ND_ARRAY = "ndArray"
    SEQUENCE = "sequence"
    SHORT = "short"
    STRING = "string"
    VIEW = "view"
    VIEW_GROUP = "viewGroupEntry"


class ArgumentTypeEnum(Enum):
    ARRAY = "SHAPELETS_ARRAY"
    BOOLEAN = "BOOLEAN"
    BYTE = "BYTE"
    CAPSULE = "CAPSULE"
    DATAFRAME = "DATAFRAME"
    DOUBLE = "DOUBLE"
    FLOAT = "FLOAT"
    FUNCTION = "FUNCTION"
    IMAGE = "IMAGE"
    ALTAIR = "ALTAIR"
    INT = "INTEGER"
    LIST = "ARGUMENT_LIST"
    LONG = "LONG"
    MATCH = "MATCH"
    MODEL = "MODEL"
    ND_ARRAY = "ND_ARRAY"
    SEQUENCE = "SEQUENCE"
    SHORT = "SHORT"
    STRING = "STRING"
    VIEW = "VIEW"
    VIEW_GROUP_ENTRY = "VIEW_GROUP_ENTRY"


ReverseArgumentTypeEnumLookup = {
    ArgumentTypeEnum.ARRAY.value: ArgumentTypeEnum.ARRAY,
    ArgumentTypeEnum.BOOLEAN.value: ArgumentTypeEnum.BOOLEAN,
    ArgumentTypeEnum.BYTE.value: ArgumentTypeEnum.BYTE,
    ArgumentTypeEnum.CAPSULE.value: ArgumentTypeEnum.CAPSULE,
    ArgumentTypeEnum.DATAFRAME.value: ArgumentTypeEnum.DATAFRAME,
    ArgumentTypeEnum.DOUBLE.value: ArgumentTypeEnum.DOUBLE,
    ArgumentTypeEnum.FLOAT.value: ArgumentTypeEnum.FLOAT,
    ArgumentTypeEnum.FUNCTION.value: ArgumentTypeEnum.FUNCTION,
    ArgumentTypeEnum.IMAGE.value: ArgumentTypeEnum.IMAGE,
    ArgumentTypeEnum.INT.value: ArgumentTypeEnum.INT,
    ArgumentTypeEnum.LIST.value: ArgumentTypeEnum.LIST,
    ArgumentTypeEnum.LONG.value: ArgumentTypeEnum.LONG,
    ArgumentTypeEnum.MATCH.value: ArgumentTypeEnum.MATCH,
    ArgumentTypeEnum.MODEL.value: ArgumentTypeEnum.MODEL,
    ArgumentTypeEnum.ND_ARRAY.value: ArgumentTypeEnum.ND_ARRAY,
    ArgumentTypeEnum.SEQUENCE.value: ArgumentTypeEnum.SEQUENCE,
    ArgumentTypeEnum.SHORT.value: ArgumentTypeEnum.SHORT,
    ArgumentTypeEnum.STRING.value: ArgumentTypeEnum.STRING,
    ArgumentTypeEnum.VIEW.value: ArgumentTypeEnum.VIEW,
    ArgumentTypeEnum.VIEW_GROUP_ENTRY.value: ArgumentTypeEnum.VIEW_GROUP_ENTRY
}

ToBackendMap = {
    ArgumentTypeEnum.ARRAY: "ShapeletsArray",
    ArgumentTypeEnum.BOOLEAN: "Boolean",
    ArgumentTypeEnum.BYTE: "Byte",
    ArgumentTypeEnum.CAPSULE: "Capsule",
    ArgumentTypeEnum.DATAFRAME: "Dataframe",
    ArgumentTypeEnum.DOUBLE: "Double",
    ArgumentTypeEnum.FLOAT: "Float",
    ArgumentTypeEnum.FUNCTION: "() ->",
    ArgumentTypeEnum.IMAGE: "Image",
    ArgumentTypeEnum.ALTAIR: "Altair",
    ArgumentTypeEnum.INT: "Int",
    ArgumentTypeEnum.LIST: "List",
    ArgumentTypeEnum.LONG: "Long",
    ArgumentTypeEnum.MATCH: "Match",
    ArgumentTypeEnum.MODEL: "Model",
    ArgumentTypeEnum.ND_ARRAY: "NDArray",
    ArgumentTypeEnum.SEQUENCE: "SequenceSpec",
    ArgumentTypeEnum.SHORT: "Short",
    ArgumentTypeEnum.STRING: "String",
    ArgumentTypeEnum.VIEW: "View",
    ArgumentTypeEnum.VIEW_GROUP_ENTRY: "ViewGroupEntry"
}


def argument_type_for(value):
    if not value:
        raise ValueError("value is None")
    if isinstance(value, Capsule):
        return ArgumentTypeEnum.CAPSULE
    if isinstance(value, Dataframe):
        return ArgumentTypeEnum.DATAFRAME
    if isinstance(value, np.ndarray):
        return ArgumentTypeEnum.ARRAY
    if isinstance(value, NDArray):
        return ArgumentTypeEnum.ND_ARRAY
    if isinstance(value, Image):
        return ArgumentTypeEnum.IMAGE
    if isinstance(value, View):
        return ArgumentTypeEnum.VIEW
    if isinstance(value, ViewGroupEntry):
        return ArgumentTypeEnum.VIEW_GROUP_ENTRY
    if isinstance(value, Match):
        return ArgumentTypeEnum.MATCH
    if isinstance(value, Model):
        return ArgumentTypeEnum.MODEL
    if isinstance(value, Sequence):
        return ArgumentTypeEnum.SEQUENCE
    if isinstance(value, bool):
        return ArgumentTypeEnum.BOOLEAN
    if isinstance(value, bytes):
        return ArgumentTypeEnum.BYTE
    if isinstance(value, float):
        return ArgumentTypeEnum.DOUBLE
    if isinstance(value, int):
        return ArgumentTypeEnum.LONG
    if isinstance(value, str):
        return ArgumentTypeEnum.STRING
    if callable(value):
        return ArgumentTypeEnum.FUNCTION
    if isinstance(value, (list, tuple)):
        return ArgumentTypeEnum.LIST
    raise TypeNotSupported(f"for value: {value}, type: {type(value)}")


def is_numeric(value):
    return argument_type_for(value) in {
        ArgumentTypeEnum.DOUBLE,
        ArgumentTypeEnum.FLOAT,
        ArgumentTypeEnum.INT,
        ArgumentTypeEnum.LONG,
        ArgumentTypeEnum.SHORT
    }


def is_str(value):
    return argument_type_for(value) == ArgumentTypeEnum.STRING


def is_bool(value):
    return argument_type_for(value) == ArgumentTypeEnum.BOOLEAN


def is_dataframe(value):
    return argument_type_for(value) == ArgumentTypeEnum.DATAFRAME


def is_model(value):
    return argument_type_for(value) == ArgumentTypeEnum.MODEL


def is_sequence(value):
    return argument_type_for(value) == ArgumentTypeEnum.SEQUENCE


def is_nd_array(value):
    return argument_type_for(value) == ArgumentTypeEnum.ND_ARRAY


def is_capsule(value):
    return argument_type_for(value) == ArgumentTypeEnum.CAPSULE


def is_image(value):
    return argument_type_for(value) == ArgumentTypeEnum.IMAGE


def backend_type(arg_type: ArgumentTypeEnum) -> str:
    return ToBackendMap[arg_type]


class ArgumentType:
    SEP = ":"

    def __init__(self, *args: typing.Tuple[ArgumentTypeEnum, ...]):
        self.types = args

    def __eq__(self, other: typing.Any) -> bool:
        return (isinstance(other, ArgumentType) and
                self.types == other.types)

    def __hash__(self) -> int:
        return hash(str(self.types))

    def get(self, index: int = 0) -> ArgumentTypeEnum:
        return self.types[index]

    def get_backend(self, index: int = 0) -> str:
        return backend_type(self.get(index))

    def get_order(self) -> int:
        return len(self.types)

    def get_all_values(self) -> str:
        return ArgumentType.SEP.join(x.value for x in self.types)

    def get_inner(self) -> ArgumentType:
        return ArgumentType(*self.types[1:])

    def is_numeric(self):
        return (self.get_order() == 1 and
                self.types[0] in {
                    ArgumentTypeEnum.DOUBLE,
                    ArgumentTypeEnum.FLOAT,
                    ArgumentTypeEnum.INT,
                    ArgumentTypeEnum.LONG,
                    ArgumentTypeEnum.SHORT
                })

    def is_str(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.STRING)

    def is_bool(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.BOOLEAN)

    def is_dataframe(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.DATAFRAME)

    def is_model(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.MODEL)

    def is_image(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.IMAGE)

    def is_sequence(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.SEQUENCE)

    def is_nd_array(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.ND_ARRAY)

    def is_capsule(self):
        return (self.get_order() == 1 and
                self.types[0] == ArgumentTypeEnum.CAPSULE)

    def __str__(self):
        return self.get_all_values()

    def __repr__(self):
        return self.get_all_values()


def compatible_types_pred(src_type: ArgumentType, dst_type: ArgumentType) -> bool:
    return (src_type == dst_type or
            (src_type.get() == dst_type.get() and
             compatible_types_pred(src_type.get_inner(), dst_type.get_inner())))


def serialize_lambda(lambda_function: typing.Callable) -> str:
    """
    This function serializes the body, and closure, of a lambda function into a base64 string.
    :param lambda_function: The function to be serialised.
    :return: A base64 encoded string.
    """
    return base64.b64encode(cloudpickle.dumps(lambda_function)).decode("utf-8")


def deserialize_lambda(lambda_base64: str) -> typing.Callable:
    return pickle.loads(base64.b64decode(lambda_base64.encode('utf-8')))


class ArgumentValue(typing.Generic[SupportedTypes]):
    TYPE_KEY = "type"
    VALUE_KEY = "value"

    def __init__(self, arg_type: ArgumentType, arg_value: SupportedTypes):
        self.arg_type = arg_type
        self.arg_value = ArgumentValue.__get_value(arg_type, arg_value)
        self.__assert_valid()

    @staticmethod
    def __get_value(arg_type: ArgumentType, value: SupportedTypes) -> SupportedTypes:
        if arg_type.get() == ArgumentTypeEnum.LIST:
            return [ArgumentValue(arg_type.get_inner(), inner_value) for inner_value in value]
        return value

    def __hash__(self):
        if isinstance(self.arg_value, (np.ndarray, list)):
            return hash((str(self.arg_value), self.arg_type))
        return hash((self.arg_value, self.arg_type))

    def __eq__(self, other):
        if (isinstance(other, ArgumentValue) and
                self.arg_type == other.arg_type):
            if self.arg_type.get() == ArgumentTypeEnum.ND_ARRAY:
                return np.array_equal(self.arg_value, other.arg_value)
            return self.arg_value == other.arg_value
        return False

    def __assert_valid(self):
        arg_type_value = self.arg_type.get()
        if arg_type_value == ArgumentTypeEnum.SEQUENCE:
            is_valid = isinstance(self.arg_value, Sequence) or self.arg_value is None
        elif arg_type_value == ArgumentTypeEnum.CAPSULE:
            is_valid = isinstance(self.arg_value, Capsule)
        elif arg_type_value == ArgumentTypeEnum.DATAFRAME:
            is_valid = isinstance(self.arg_value, Dataframe)
        elif arg_type_value == ArgumentTypeEnum.IMAGE:
            is_valid = isinstance(self.arg_value, Image)
        elif arg_type_value == ArgumentTypeEnum.ARRAY:
            is_valid = isinstance(self.arg_value, np.ndarray)
        elif arg_type_value == ArgumentTypeEnum.ND_ARRAY:
            is_valid = isinstance(self.arg_value, NDArray) or self.arg_value is None
        elif arg_type_value == ArgumentTypeEnum.VIEW:
            is_valid = isinstance(self.arg_value, View)
        elif arg_type_value == ArgumentTypeEnum.VIEW_GROUP_ENTRY:
            is_valid = isinstance(self.arg_value, ViewGroupEntry)
        elif arg_type_value == ArgumentTypeEnum.MATCH:
            is_valid = isinstance(self.arg_value, Match)
        elif arg_type_value == ArgumentTypeEnum.MODEL:
            is_valid = isinstance(self.arg_value, Model)
        elif arg_type_value == ArgumentTypeEnum.FUNCTION:
            is_valid = callable(self.arg_value)
        elif arg_type_value == ArgumentTypeEnum.BOOLEAN:
            is_valid = isinstance(self.arg_value, bool)
        elif arg_type_value == ArgumentTypeEnum.LIST:
            is_valid = isinstance(self.arg_value, list)
            is_valid = is_valid and isinstance(self.arg_value[0], ArgumentValue) if self.arg_value else True
        elif arg_type_value == ArgumentTypeEnum.BYTE:
            is_valid = isinstance(self.arg_value, (bytes, bytearray))
        elif arg_type_value in (ArgumentTypeEnum.DOUBLE,
                                ArgumentTypeEnum.INT,
                                ArgumentTypeEnum.LONG,
                                ArgumentTypeEnum.SHORT,
                                ArgumentTypeEnum.FLOAT):
            is_valid = isinstance(self.arg_value, (int, float)) or self.arg_value is None
        elif arg_type_value == ArgumentTypeEnum.STRING:
            is_valid = isinstance(self.arg_value, str)
        else:
            raise InvalidArgumentValue(f"unknown argument type for value {self.arg_value}.")
        if not is_valid:
            raise InvalidArgumentValue(
                f"Types '{arg_type_value.value}' and '{type(self.arg_value).__name__}' don't match.")

    def to_dict(self) -> dict:
        arg_type_enum = self.arg_type.get()
        res = {ArgumentValue.TYPE_KEY: arg_type_enum.value}
        if arg_type_enum == ArgumentTypeEnum.SEQUENCE:
            res[AttributeNames.SEQUENCE.value] = {"id": self.arg_value.sequence_id}
        elif arg_type_enum == ArgumentTypeEnum.DATAFRAME:
            res[AttributeNames.DATAFRAME.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.ND_ARRAY:
            res[AttributeNames.ND_ARRAY.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.CAPSULE:
            res[AttributeNames.CAPSULE.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.IMAGE:
            res[AttributeNames.IMAGE.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.VIEW:
            res[AttributeNames.VIEW.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.VIEW_GROUP_ENTRY:
            res[AttributeNames.VIEW_GROUP.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.MATCH:
            res[AttributeNames.MATCH.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.MODEL:
            res[AttributeNames.MODEL.value] = self.arg_value.to_dict()
        elif arg_type_enum == ArgumentTypeEnum.FUNCTION:
            res[AttributeNames.FUNCTION.value] = serialize_lambda(self.arg_value)
        elif arg_type_enum == ArgumentTypeEnum.BOOLEAN:
            res[AttributeNames.BOOL.value] = self.arg_value
        elif arg_type_enum == ArgumentTypeEnum.BYTE:
            res[AttributeNames.BYTE.value] = self.arg_value
        elif arg_type_enum == ArgumentTypeEnum.LIST:
            res[AttributeNames.LIST.value] = [inner_value.to_dict() for inner_value in self.arg_value]
        elif arg_type_enum == ArgumentTypeEnum.DOUBLE:
            res[AttributeNames.DOUBLE.value] = self.arg_value
        elif arg_type_enum == ArgumentTypeEnum.FLOAT:
            res[AttributeNames.FLOAT.value] = self.arg_value
        elif arg_type_enum == ArgumentTypeEnum.INT:
            res[AttributeNames.INT.value] = self.arg_value
        elif arg_type_enum == ArgumentTypeEnum.LONG:
            res[AttributeNames.LONG.value] = self.arg_value
        elif arg_type_enum == ArgumentTypeEnum.SHORT:
            res[AttributeNames.SHORT.value] = self.arg_value
        elif arg_type_enum == ArgumentTypeEnum.STRING:
            res[AttributeNames.STRING.value] = self.arg_value
        else:
            raise InvalidArgumentValue(f"Argument Type '{arg_type_enum}' not supported")
        return res

    @staticmethod
    def from_dict(input_: typing.Dict):
        arg_type_enum = ReverseArgumentTypeEnumLookup.get(input_[ArgumentValue.TYPE_KEY])
        if not arg_type_enum:
            arg_type_enum = ArgumentTypeEnum[input_[ArgumentValue.TYPE_KEY]]
        arg_inner_type_enum = None
        if arg_type_enum == ArgumentTypeEnum.SEQUENCE:
            arg_value = Sequence.from_dict(input_[AttributeNames.SEQUENCE.value])
        elif arg_type_enum == ArgumentTypeEnum.DATAFRAME:
            arg_value = Dataframe.from_dict(input_[AttributeNames.DATAFRAME.value])
        elif arg_type_enum == ArgumentTypeEnum.ND_ARRAY:
            arg_value = NDArray.from_dict(input_[AttributeNames.ND_ARRAY.value])
        elif arg_type_enum == ArgumentTypeEnum.CAPSULE:
            arg_value = Capsule.from_dict(input_[AttributeNames.CAPSULE.value])
        elif arg_type_enum == ArgumentTypeEnum.IMAGE:
            arg_value = Image.from_dict(input_[AttributeNames.IMAGE.value])
        elif arg_type_enum == ArgumentTypeEnum.VIEW:
            arg_value = View.from_dict(input_[AttributeNames.VIEW.value])
        elif arg_type_enum == ArgumentTypeEnum.VIEW_GROUP_ENTRY:
            arg_value = ViewGroupEntry.from_dict(input_[AttributeNames.VIEW_GROUP.value])
        elif arg_type_enum == ArgumentTypeEnum.MATCH:
            arg_value = Match.from_dict(input_[AttributeNames.MATCH.value])
        elif arg_type_enum == ArgumentTypeEnum.MODEL:
            arg_value = Model.from_dict(input_[AttributeNames.MODEL.value])
        elif arg_type_enum == ArgumentTypeEnum.FUNCTION:
            arg_value = deserialize_lambda(input_[AttributeNames.FUNCTION.value])
        elif arg_type_enum == ArgumentTypeEnum.BOOLEAN:
            arg_value = bool(input_[AttributeNames.BOOL.value])
        elif arg_type_enum == ArgumentTypeEnum.BYTE:
            arg_value = bytes(input_[AttributeNames.BYTE.value])
        elif arg_type_enum == ArgumentTypeEnum.LIST:
            arg_value = []
            input_list = copy.deepcopy(input_[AttributeNames.LIST.value])
            for list_item in input_list:
                type_value = list_item[ArgumentValue.TYPE_KEY]
                arg_inner_type_enum = ReverseArgumentTypeEnumLookup[type_value]
                list_item[ArgumentValue.TYPE_KEY] = arg_inner_type_enum.name
                arg_value.append(ArgumentValue.from_dict(list_item).arg_value)
        elif arg_type_enum == ArgumentTypeEnum.DOUBLE:
            arg_value = float(input_[AttributeNames.DOUBLE.value])
        elif arg_type_enum == ArgumentTypeEnum.FLOAT:
            arg_value = float(input_[AttributeNames.FLOAT.value])
        elif arg_type_enum == ArgumentTypeEnum.INT:
            arg_value = int(input_[AttributeNames.INT.value])
        elif arg_type_enum == ArgumentTypeEnum.LONG:
            arg_value = int(input_[AttributeNames.LONG.value])
        elif arg_type_enum == ArgumentTypeEnum.SHORT:
            arg_value = int(input_[AttributeNames.SHORT.value])
        elif arg_type_enum == ArgumentTypeEnum.STRING:
            arg_value = input_[AttributeNames.STRING.value]
        else:
            raise InvalidArgumentValue(f"Argument Type '{arg_type_enum}' not supported")
        if arg_inner_type_enum:
            arg_type = ArgumentType(arg_type_enum, arg_inner_type_enum)
        else:
            arg_type = ArgumentType(arg_type_enum)
        return ArgumentValue(arg_type, arg_value)

    def __repr__(self):
        return f"{self.arg_type} -> {self.arg_value}"
