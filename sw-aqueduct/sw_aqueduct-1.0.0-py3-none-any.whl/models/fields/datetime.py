# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class BaseDateTimeFieldType(BaseField):
    defaultValueType: typing.AnyStr = field()
    calculatedDiff: bool = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["Date", "date"]))
    required: bool = field()
    readOnly: bool = field()
    supportsMultipleOutputMappings: bool = field()


@define
class DateTimeField(BaseDateTimeFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["DateTime", "dateTime"]))
    futurePastType: typing.AnyStr = field(default=None)
    futurePastValue: int = field(default=None)
    required: bool = field(default=None)
    readOnly: bool = field(default=None)


@define
class TimespanField(BaseDateTimeFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Timespan", "timespan"]))


@define
class DateField(BaseDateTimeFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Date", "date"]))


@define
class TimeField(BaseDateTimeFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Time", "time"]))


@define
class FirstCreatedField(BaseDateTimeFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["FirstCreated"]))


@define
class LastUpdatedField(BaseDateTimeFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["LastUpdated", "lastUpdated"]))
