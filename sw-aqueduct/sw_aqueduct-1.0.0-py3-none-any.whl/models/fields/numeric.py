# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class NumericField(BaseField):
    step: int = field()
    unique: bool = field()
    prefix: typing.AnyStr = field()
    suffix: typing.AnyStr = field()
    format: typing.AnyStr = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["Numeric", "numeric"]))
    required: bool = field()
    readOnly: bool = field()
    supportsMultipleOutputMappings: bool = field()
