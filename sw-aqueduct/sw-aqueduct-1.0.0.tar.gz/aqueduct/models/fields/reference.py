# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class BaseReferenceFieldType(BaseField):
    targetId: typing.AnyStr = field()
    columns: typing.List = field()
    canAdd: bool = field()
    createBackreference: bool = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["Reference", "reference"]))
    required: bool = field()
    readOnly: bool = field()
    supportsMultipleOutputMappings: bool = field()


@define
class SingleSelectReferenceField(BaseReferenceFieldType):
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Single", "single"]))


@define
class MultiSelectReferenceField(BaseReferenceFieldType):
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Multi", "multi"]))


@define
class GridReferenceField(BaseReferenceFieldType):
    controlType: typing.AnyStr = field(validator=validators.in_(["Grid", "grid"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Multi", "multi"]))
