# -*- coding: utf-8 -*-
from typing import AnyStr, List

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from attr import define, field


@define
class InputOutputFieldMapping:
    addMissing: bool = field()
    unixEpochUnit: AnyStr = field()
    enableDeletionOnNull: bool = field()
    dataFormat: AnyStr = field()
    listModificationType: AnyStr = field()
    key: AnyStr = field(factory=str)  # Some tasks in 10.4.0 do not contain this key so moving to optional
    userFormat: AnyStr = field(default=None)
    subValue: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="InputOutputFieldMapping")


@define
class OutputMapping(InputOutputFieldMapping):
    type: AnyStr = field(default=None)
    value: AnyStr = field(default=None)
    example: AnyStr = field(default=None)
    parserType: AnyStr = field(default=None)
    expression: AnyStr = field(default=None)
    customDataFormat: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="OutputMapping")


@define
class Output:
    type: AnyStr = field()
    mappings: List[OutputMapping] = field(default=[])
    createType: AnyStr = field(default=None)
    errorHandlingType: AnyStr = field(default=None)
    keyFieldId: AnyStr = field(default=None)
    applicationId: AnyStr = field(default=None)
    backReferenceFieldId: AnyStr = field(default=None)
    customDataFormat: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="Output")

    def __attrs_post_init__(self):
        if self.mappings:
            return_list = []
            for item in self.mappings:
                try:
                    return_list.append(OutputMapping(**item))
                except Exception as e:
                    raise e
            self.mappings = return_list


@define
class InputMapping(InputOutputFieldMapping):
    example: AnyStr = field(default=None)
    type: AnyStr = field(default=None)
    value: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="InputMapping")


@define
class Action:
    type: AnyStr = field()
    descriptor: dict = field()
    readonly: bool = field()
    script: AnyStr = field(default=None)
    packageDescriptorId: AnyStr = field(default=None)
    assetId: AnyStr = field(default=None)
    forkedFromPackage: AnyStr = field(default=None)
    assetDependencyType: AnyStr = field(default=None)
    assetDependencyVersion: AnyStr = field(default=None)
    headers: dict = field(default={})  # Identified in a task from 10.4.3
    parameters: dict = field(default={})  # Identified in a task from 10.4.3
    authenticationParameters: dict = field(default={})  # Identified in a task from 10.4.3
    requestType: AnyStr = field(default=None)  # Identified in a task from 10.4.3
    apiType: AnyStr = field(default=None)  # Identified in a task from 10.4.3
    authenticationType: AnyStr = field(default=None)  # Identified in a task from 10.4.3

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="Action")

    def __attrs_post_init__(self):
        if self.descriptor:
            from .plugin import ActionDescriptor

            try:
                self.descriptor = ActionDescriptor(**self.descriptor)
            except Exception as e:
                raise e


@define
class Task:
    action: Action = field()
    isSystemTask: bool = field()
    createdDate: AnyStr = field()
    modifiedDate: AnyStr = field()
    valid: bool = field()
    uid: AnyStr = field()
    version: int = field()
    id: AnyStr = field()
    name: AnyStr = field()
    disabled: bool = field()
    applicationId: AnyStr = field(default=None)
    description: AnyStr = field(default=None)
    createdByUser: dict = field(default={})
    modifiedByUser: dict = field(default={})
    inputMapping: List[InputMapping] = field(default=[])
    outputs: List[Output] = field(default=[])
    triggers: List = field(default=[])
    actionType: AnyStr = field(default=None)
    actionDescription: AnyStr = field(default=None)
    actionDescriptorImageId: AnyStr = field(default=None)
    actionDescriptorName: AnyStr = field(default=None)
    actionDescriptorVendor: AnyStr = field(default=None)
    actionDescriptorProduct: AnyStr = field(default=None)
    actionDescriptorVersion: AnyStr = field(default=None)
    customDataFormat: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="Task")

    def __attrs_post_init__(self):
        if self.inputMapping:
            return_list = []
            for item in self.inputMapping:
                try:
                    return_list.append(InputMapping(**item))
                except Exception as e:
                    raise e
            self.inputMapping = return_list
        if self.outputs:
            return_list = []
            for item in self.outputs:
                try:
                    return_list.append(Output(**item))
                except Exception as e:
                    raise e
            self.outputs = return_list
        if self.action:
            try:
                self.action = Action(**self.action)
            except Exception as e:
                raise e


@define
class TaskLight:
    id: AnyStr = field()
    name: AnyStr = field()
    disabled: bool = field()
    actionType: AnyStr = field()
    actionDescription: AnyStr = field()
    actionDescriptorImageId: AnyStr = field()
    actionDescriptorName: AnyStr = field()
    valid: bool = field()
    migrated: bool = field(default=None)
    deprecated: bool = field(default=None)
    applicationId: AnyStr = field(default=None)
    actionDescriptorVendor: AnyStr = field(default=None)
    actionDescriptorProduct: AnyStr = field(default=None)
    actionDescriptorVersion: AnyStr = field(default=None)
    description: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="TaskLight")
