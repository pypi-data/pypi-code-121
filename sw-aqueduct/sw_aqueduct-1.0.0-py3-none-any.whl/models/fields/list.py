# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class BaseListFieldType(BaseField):
    itemLengthType: typing.AnyStr = field()
    itemStep: int = field()
    searchPath: typing.AnyStr = field()
    searchPathIsArray: bool = field()
    searchPathCollectionExtension: typing.AnyStr = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["List", "list"]))
    required: bool = field()
    readOnly: bool = field()
    supportsMultipleOutputMappings: bool = field()


@define
class TextListField(BaseListFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Text", "text"]))


@define
class NumericListField(BaseListFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Numeric", "numeric"]))
