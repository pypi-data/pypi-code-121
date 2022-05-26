# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class BaseTextFieldType(BaseField):

    lengthType: typing.AnyStr = field()
    visualize: bool = field()
    visualizeMode: int = field()
    required: bool = field()
    readOnly: bool = field()
    supportsMultipleOutputMappings: bool = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["Text", "text"]))


@define
class MultilineField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Multiline", "multiline"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)


@define
class TextField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Text", "text"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)


@define
class EmailField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Email", "email"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)


@define
class TelephoneField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Telephone", "telephone"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)


@define
class UrlField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["URL", "url"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)


@define
class IPField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["IP", "ip"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)


@define
class RichTextField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["Rich", "rich"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)


@define
class JSONField(BaseTextFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["JSON", "json"]))
    prefix: typing.AnyStr = field(default=None)
    suffix: typing.AnyStr = field(default=None)
    placeholder: typing.AnyStr = field(default=None)
    unique: bool = field(default=None)
