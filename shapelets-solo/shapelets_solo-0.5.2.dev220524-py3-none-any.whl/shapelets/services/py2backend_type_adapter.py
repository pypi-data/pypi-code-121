# Copyright (c) 2020 Shapelets.io
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this

from enum import Enum
import typing

from shapelets.dsl.argument_types import (
    ArgumentTypeEnum,
    ArgumentType,
    backend_type
)
from shapelets.model import (
    Match,
    Sequence,
    View,
    ViewGroupEntry,
    ReplicatedParam,
    NDArray, Dataframe, Model, Capsule, Image, Altair
)


class TransformMode(Enum):
    SHAPELETS_WORKER = "ShapeletsWorker"
    KOTLIN = "KOTLIN"


OUTPUT_LIST_RETURN_TYPE = "OutputList"


def transform_type(param: type, mode: TransformMode) -> str:
    if mode is TransformMode.SHAPELETS_WORKER:
        return __transform_worker_mode(param)
    if mode is TransformMode.KOTLIN:
        return __transform_kotlin_mode(param)
    raise ValueError(f"transform_type unknown mode {mode}, param {param}")


def __transform_worker_mode(param: type) -> str:
    if param is Sequence:
        return ArgumentTypeEnum.SEQUENCE.value
    if param is NDArray:
        return ArgumentTypeEnum.ND_ARRAY.value
    if param is Dataframe:
        return ArgumentTypeEnum.DATAFRAME.value
    if param is Image:
        return ArgumentTypeEnum.IMAGE.value
    if param is Altair:
        return ArgumentTypeEnum.ALTAIR.value
    if param is Model:
        return ArgumentTypeEnum.MODEL.value
    if param is Capsule:
        return ArgumentTypeEnum.CAPSULE.value
    if param is View:
        return ArgumentTypeEnum.VIEW.value
    if param is ViewGroupEntry:
        return ArgumentTypeEnum.VIEW_GROUP_ENTRY.value
    if param is Match:
        return ArgumentTypeEnum.MATCH.value
    if param is bool:
        return ArgumentTypeEnum.BOOLEAN.value
    if param is float:
        return ArgumentTypeEnum.FLOAT.value
    if param is str:
        return ArgumentTypeEnum.STRING.value
    if param is int:
        return ArgumentTypeEnum.INT.value
    if (isinstance(param, typing._GenericAlias) and  # pylint: disable=W0212
            param.__origin__ in (typing.List.__origin__, typing.Sequence.__origin__)):
        return f"{OUTPUT_LIST_RETURN_TYPE}({__transform_worker_mode(param.__args__[0])})"
    if (isinstance(param, typing._GenericAlias) and  # pylint: disable=W0212
            param.__origin__ is ReplicatedParam):
        return __transform_worker_mode(param.__args__[0])
    raise ValueError(f"shapelets worker type not supported: {param}")


def __transform_kotlin_mode(param: type) -> str:
    if param is Sequence:
        return backend_type(ArgumentTypeEnum.SEQUENCE)
    if param is Dataframe:
        return backend_type(ArgumentTypeEnum.DATAFRAME)
    if param is Model:
        return backend_type(ArgumentTypeEnum.MODEL)
    if param is Image:
        return backend_type(ArgumentTypeEnum.IMAGE)
    if param is Altair:
        return backend_type(ArgumentTypeEnum.ALTAIR)
    if param is Capsule:
        return backend_type(ArgumentTypeEnum.CAPSULE)
    if param is View:
        return backend_type(ArgumentTypeEnum.VIEW)
    if param is ViewGroupEntry:
        return backend_type(ArgumentTypeEnum.VIEW_GROUP_ENTRY)
    if param is Match:
        return backend_type(ArgumentTypeEnum.MATCH)
    if param is bool:
        return backend_type(ArgumentTypeEnum.BOOLEAN)
    if param is float:
        return backend_type(ArgumentTypeEnum.DOUBLE)
    if param is str:
        return backend_type(ArgumentTypeEnum.STRING)
    if param is int:
        return backend_type(ArgumentTypeEnum.INT)
    if param is NDArray:
        return backend_type(ArgumentTypeEnum.ND_ARRAY)
    if (isinstance(param, typing._GenericAlias) and  # pylint: disable=W0212
            param.__origin__ in (typing.List.__origin__, typing.Sequence.__origin__)):
        be_type = backend_type(ArgumentTypeEnum.LIST)
        inner_type = __transform_kotlin_mode(param.__args__[0])
        return f"{be_type}{ArgumentType.SEP}{inner_type}"
    if (isinstance(param, typing._GenericAlias) and  # pylint: disable=W0212
            param.__origin__ is ReplicatedParam):
        return __transform_kotlin_mode(param.__args__[0])
    raise ValueError(f"backend type not supported: {param}")
