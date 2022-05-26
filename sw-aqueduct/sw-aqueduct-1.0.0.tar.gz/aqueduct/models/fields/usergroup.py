# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import BaseField


@define
class BaseUserGroupFieldType(BaseField):
    showAllUsers: bool = field()
    showAllGroups: bool = field()
    members: typing.List = field()
    defaults: typing.List = field()
    searchPath: typing.AnyStr = field()
    searchPathIsArray: bool = field()
    sortPath: typing.AnyStr = field()
    fieldType: typing.AnyStr = field(validator=validators.in_(["UserGroup", "userGroup"]))
    supportsMultipleOutputMappings: bool = field()


@define
class UserGroupField(BaseUserGroupFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["UserGroup", "userGroup"]))
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Single", "single"]))
    searchPathCollectionExtension: typing.AnyStr = field(default=None)
    required: bool = field(default=None)
    readOnly: bool = field(default=None)


@define
class UsersGroupsField(BaseUserGroupFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["UserGroup", "userGroup"]))
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Multi", "multi"]))
    searchPathCollectionExtension: typing.AnyStr = field(default=None)
    required: bool = field(default=None)
    readOnly: bool = field(default=None)


@define
class CreatedByField(BaseUserGroupFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["CreatedBy", "createdBy"]))
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Single", "single"]))
    searchPathCollectionExtension: typing.AnyStr = field(default=None)
    required: bool = field(default=None)
    readOnly: bool = field(default=None)
    reverseValueMap: dict = field(default={})


@define
class LastUpdatedByField(BaseUserGroupFieldType):
    inputType: typing.AnyStr = field(validator=validators.in_(["LastUpdatedBy", "lastUpdatedBy"]))
    controlType: typing.AnyStr = field(validator=validators.in_(["Select", "select"]))
    selectionType: typing.AnyStr = field(validator=validators.in_(["Single", "single"]))
    searchPathCollectionExtension: typing.AnyStr = field(default=None)
    required: bool = field(default=None)
    readOnly: bool = field(default=None)
    reverseValueMap: dict = field(default={})
