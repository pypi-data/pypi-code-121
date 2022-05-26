# -*- coding: utf-8 -*-
from typing import AnyStr

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from attr import define, field


@define
class AssetBase:
    type: AnyStr = field()
    pythonVersion: AnyStr = field()
    id: AnyStr = field()
    version: int = field()
    name: AnyStr = field()
    disabled: bool = field()


@define
class Descriptor(AssetBase):
    base64Image: AnyStr = field()
    family: AnyStr = field()
    description: AnyStr = field()
    testScript: AnyStr = field()
    testScriptFile: AnyStr = field()
    imageId: AnyStr = field()
    inputParameters: dict = field(default={})
    packageDescriptor: dict = field(default={})

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="Descriptor")

    def __attrs_post_init__(self):
        if self.packageDescriptor:
            from .plugin import Plugin

            try:
                self.packageDescriptor = Plugin(**self.packageDescriptor)
            except Exception as e:
                raise e


@define
class Asset(AssetBase):
    valid: bool = field()
    uid: AnyStr = field()
    parameters: dict = field(default={})
    descriptor: Descriptor = field(default={})
    description: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="Asset")
