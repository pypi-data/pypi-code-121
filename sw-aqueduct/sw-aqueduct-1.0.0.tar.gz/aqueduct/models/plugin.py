# -*- coding: utf-8 -*-
from typing import AnyStr, List

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from attr import define, field


@define
class BaseDescriptor:
    name: AnyStr = field()
    base64Image: AnyStr = field()
    description: AnyStr = field()
    version: AnyStr = field()
    pythonVersion: AnyStr = field()
    disabled: bool = field()
    id: AnyStr = field()

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="BaseDescriptor")


@define
class Plugin(BaseDescriptor):
    author: AnyStr = field()
    modifiedDate: AnyStr = field()
    createdDate: AnyStr = field()
    authorEmail: AnyStr = field()
    url: AnyStr = field()
    packages: List = field()
    fileId: AnyStr = field()
    isEmailBundle: bool = field()
    vendor: AnyStr = field()
    product: AnyStr = field()
    readme: AnyStr = field()
    changeLog: AnyStr = field()
    supportedSwimlaneVersion: AnyStr = field(
        factory=str
    )  # Swimlane 10.4.0 does not have this field so its not required
    availableActionDescriptors: List = field(default=[])
    assetDescriptors: List = field(default=[])
    family: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="Plugin")

    def __attrs_post_init__(self):
        if self.assetDescriptors:
            return_list = []
            for item in self.assetDescriptors:
                try:
                    return_list.append(AssetDescriptor(**item))
                except Exception as e:
                    raise e
            self.assetDescriptors = return_list
        if self.availableActionDescriptors:
            return_list = []
            for item in self.availableActionDescriptors:
                try:
                    return_list.append(ActionDescriptor(**item))
                except Exception as e:
                    raise e
            self.availableActionDescriptors = return_list


@define
class PackageDescriptor(Plugin):
    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="PackageDescriptor")


@define
class PackageDescriptor2:
    disabled: bool = field()
    id: AnyStr = field()
    isEmailBundle: bool = field()
    modifiedDate: AnyStr = field()
    createdDate: AnyStr = field()

    name: AnyStr = field(factory=str)
    base64Image: AnyStr = field(factory=str)
    description: AnyStr = field(factory=str)
    version: AnyStr = field(factory=str)
    pythonVersion: AnyStr = field(factory=str)
    author: AnyStr = field(factory=str)
    author_email: AnyStr = field(factory=str)
    supported_swimlane_version: AnyStr = field(factory=str)
    url: AnyStr = field(factory=str)
    packages: List = field(factory=list)
    fileId: AnyStr = field(factory=str)
    vendor: AnyStr = field(factory=str)
    product: AnyStr = field(factory=str)
    readme: AnyStr = field(default=None)
    changeLog: AnyStr = field(default=None)
    family: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="PackageDescriptor2")


@define
class License:
    package: AnyStr = field()
    license: AnyStr = field()

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="License")


@define
class ActionDescriptor:
    name: AnyStr = field()
    base64Image: AnyStr = field()
    description: AnyStr = field()
    pythonVersion: AnyStr = field()
    disabled: bool = field()
    id: AnyStr = field()
    actionType: AnyStr = field()
    readonly: bool = field()
    availableOutputTypes: List = field()
    modifiedDate: AnyStr = field()
    createdDate: AnyStr = field()
    imageId: AnyStr = field(default=None)
    scriptFile: AnyStr = field(default=None)
    version: AnyStr = field(default=None)
    script: AnyStr = field(default=None)
    licenses: List[License] = field(default=[])
    packageDescriptor: PackageDescriptor2 = field(default={})
    pythonDependencies: dict = field(default={})
    inputParameters: dict = field(default={})
    availableOutputVariables: dict = field(default={})
    family: AnyStr = field(default=None)
    assetDependencyType: AnyStr = field(default=None)
    assetDependencyVersion: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="ActionDescriptor")

    def __attrs_post_init__(self):
        if self.licenses:
            return_list = []
            for item in self.licenses:
                try:
                    return_list.append(License(**item))
                except Exception as e:
                    raise e
            self.licenses = return_list
        if self.packageDescriptor:
            try:
                self.packageDescriptor = PackageDescriptor2(**self.packageDescriptor)
            except Exception as e:
                raise e


@define
class AssetDescriptor(BaseDescriptor):
    type: AnyStr = field()
    testScript: AnyStr = field()
    testScriptFile: AnyStr = field()
    imageId: AnyStr = field()
    packageDescriptor: PackageDescriptor = field(default={})
    inputParameters: dict = field(default={})
    family: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="AssetDescriptor")


@define
class PluginLight:
    author: AnyStr = field()
    base64Image: AnyStr = field()
    changeLog: AnyStr = field()
    createdDate: AnyStr = field()
    description: AnyStr = field()
    id: AnyStr = field()
    modifiedDate: AnyStr = field()
    name: AnyStr = field()
    product: AnyStr = field()
    pythonVersion: AnyStr = field()
    readme: AnyStr = field()
    vendor: AnyStr = field()
    version: AnyStr = field()
    supportedSwimlaneVersion: AnyStr = field(default=None)
    family: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="PluginLight")
