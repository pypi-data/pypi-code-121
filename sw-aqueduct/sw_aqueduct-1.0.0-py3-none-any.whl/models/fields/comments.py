# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class CommentsField(BaseField):
    fieldType: typing.AnyStr = field(validator=validators.in_(["Comments", "comments"]))
    supportsMultipleOutputMappings: bool = field(default=None)
    required: bool = field(default=None)
    readOnly: bool = field(default=None)
