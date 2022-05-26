# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class BaseFieldValuesListType:
    id: typing.AnyStr = field()
    name: typing.AnyStr = field()
    selected: bool = field(eq=False, order=False)
    description: typing.AnyStr = field(default=None)
    otherText: typing.AnyStr = field(default=None)
    otherTextDescription: typing.AnyStr = field(default=None)
    otherTextDefaultValue: typing.AnyStr = field(default=None)
    otherTextRequired: bool = field(default=None)


@define
class BaseValuesListFieldType(BaseField):
    valueMap: dict = field()
    searchPath: typing.AnyStr = field()
    searchPathIsArray: bool = field()
    searchPathCollectionExtension: typing.AnyStr = field()
    sortPath: typing.AnyStr = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["ValuesList", "valuesList"]))
    supportsMultipleOutputMappings: bool = field()


@define
class SingleSelectField(BaseValuesListFieldType):
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Single", "single"]))
    values: typing.List[BaseFieldValuesListType] = field(default=[])
    required: bool = field(default=None)
    readOnly: bool = field(default=None)


@define
class MultiSelectField(BaseValuesListFieldType):
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Multi", "multi"]))
    values: typing.List[BaseFieldValuesListType] = field(default=[])
    required: bool = field(default=None)
    readOnly: bool = field(default=None)


@define
class RadioButtonField(BaseValuesListFieldType):
    controlType: typing.AnyStr = field(validator=validators.in_(["Radio", "radio"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Single", "single"]))
    values: typing.List[BaseFieldValuesListType] = field(default=[])
    required: bool = field(default=None)
    readOnly: bool = field(default=None)


@define
class CheckboxField(BaseValuesListFieldType):
    controlType: typing.AnyStr = field(validator=validators.in_(["Checkbox", "checkbox"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Multi", "multi"]))
    values: typing.List[BaseFieldValuesListType] = field(default=[])
    required: bool = field(default=None)
    readOnly: bool = field(default=None)
