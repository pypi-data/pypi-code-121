# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 27th 2020

This module contains the "yaml" configurable controller classes for hyssop application.

    - to create and setup controller api:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                controller/
                    __init__.py
                    foo.py

        1. "__init__.py" defines the controllers:
            from hyssop.project.web.controller import ControllerType

            class ExControllerType(ControllerType):
                Foo = ('foo', 'foo', 'Foo')

        2. "foo.py" contains the controller class:

            from hyssop.project.web.controller.tornado import RequestController

            class Foo(RequestController):

                def initialize(self, p1, **kwds):
                    self.p1 = p1

                async def get(self):
                    self.write('Hello Workd: ', self.p1)

        3. setup component block of "server_config.yaml" to tell hyssop server load the extend components "Foo":

            controller:                 # block to setup controllers
                /foo:                   # api route
                    enum: foo           # tells to load foo controller class
                    params:
                        p1: xxxx        # parameter p1 of Foo.initialize()

Modified By: hsky77
Last Updated: November 22nd 2020 14:19:18 pm
'''

from typing import List, Dict

from ...util import join_path, join_to_abs_path, BaseLocal, DynamicTypeEnum
from ..constants import Controller_Module_Folder, LocalCode_Failed_To_Load_Controller
from .config import ConfigControllerValidator


class ControllerType(DynamicTypeEnum):
    """base abstract controller enum class"""
    @staticmethod
    def get_controller_enum_class() -> List[DynamicTypeEnum]:
        try:
            return DynamicTypeEnum.get_dynamic_class_enum_class(Controller_Module_Folder)
        except:
            pass


def _get_controller_enum(key: str, contoller_types: List[ControllerType]) -> DynamicTypeEnum:
    for contoller_type in contoller_types:
        try:
            return contoller_type(key)
        except:
            continue


def get_project_controllers(server_setting: Dict, server_dir: str = None) -> List:
    controllers = []
    if Controller_Module_Folder in server_setting and isinstance(server_setting[Controller_Module_Folder], dict):
        contoller_types = []
        try:
            contoller_types = ControllerType.get_controller_enum_class()
        except:
            pass

        # validate controller config
        ConfigControllerValidator(server_setting[Controller_Module_Folder])

        for path, v in server_setting[Controller_Module_Folder].items():
            if 'enum' in v:
                t = _get_controller_enum(v['enum'], contoller_types)
                if t is None:
                    raise ImportError(BaseLocal.get_message(
                        LocalCode_Failed_To_Load_Controller, server_dir, v['enum']))
                try:
                    cls_type = t.import_class()
                except:
                    cls_type = t.import_function()

                params = v['params'] if 'params' in v and v['params'] is not None else {}

                controllers.append((path, cls_type, params))

    return controllers
