# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class TrackingField(BaseField):
    prefix: typing.AnyStr = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["Tracking", "tracking"]))
    readOnly: bool = field()
    supportsMultipleOutputMappings: bool = field()
