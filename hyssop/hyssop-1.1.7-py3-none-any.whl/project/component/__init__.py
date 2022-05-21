# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

This module contains the "yaml" configurable component classes for hyssop application.

    - to create Project components:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                component/
                    __init__.py
                    foo.py

        1. use ComponentTypes enum class to define the extend components such as:

            class ComponentExtension(ComponentTypes):
                # tuple(<component_key>, <package_route>, <class_name_in_the_py_file>)

                Foo = ('foo', 'foo', 'Foo')

        2. in "foo.py" contains the class code:

            from hyssop.project.component import Component, ComponentManager
            from . import ComponentExtension

            class Foo(Component):
                def __init__(self):
                    super().__init__(ComponentExtension.Foo)

                def init(self, component_manager: ComponentManager, p1, *arugs, **kwargs) -> None:
                    self.p1 = p1

        3. setup component block of "server_config.yaml" to tell hyssop server load the extend components "Foo":

            component:              # block to setup component
                foo:                # component_key to load
                    p1: xxxx        # parameter p1 of Foo.init()

Modified By: hsky77
Last Updated: May 21st 2022 09:59:28 am
'''

from typing import Dict, List, Union

from .base import ComponentTypes, Component, ComponentManager
from ...util import BaseLocal
from ..constants import LocalCode_Component_Duplicated_Key, LocalCode_Failed_To_Load_Component

from .config import ConfigComponentValidator


class DefaultComponentTypes(ComponentTypes):
    """server loads all components of this enum type when start"""

    Localization = ('localization', 'default', 'LocalizationComponent')
    Logger = ['logger', 'default', 'LoggerComponent']
    Callback = ('callback', 'default', 'CallbackComponent')
    Executor = ('executor', 'default', 'ExecutorComponent')


DefaultComponentEnums = [DefaultComponentTypes]


def add_default_component_types(component_type: ComponentTypes):
    DefaultComponentEnums.insert(0, component_type)


def __create_optional_components(component_manager: ComponentManager, component_settings: Dict, component_types: ComponentTypes, project_dir: str) -> None:
    for key in component_settings:
        for component_type in component_types:
            comp_type = None
            try:
                comp_type = component_type(key)
            except:
                continue
            if comp_type is not None:
                comp = comp_type.import_class()(comp_type)
                component_manager.set_component(comp)
                break

    for key in component_settings:
        comp_type = None
        for component_type in component_types:
            try:
                comp_type = component_type(key)
                break
            except:
                continue

        if comp_type:
            component_manager.invoke(comp_type, 'init',
                                     component_manager,
                                     **(component_settings[comp_type.enum_key] or {}),
                                     project_dir=project_dir)


def create_component_manager(project_dir: str, component_settings: Union[Dict, None] = None) -> ComponentManager:
    component_manager = ComponentManager()

    # extensions
    ext_comp_types = ComponentTypes.get_component_enum_class()

    # default components
    for default_enums in DefaultComponentEnums:
        for default_type in default_enums:
            comp = default_type.import_class()(default_type)
            component_manager.set_component(comp)

    # init
    for default_enums in DefaultComponentEnums:
        for default_type in default_enums:
            if component_settings and default_type.enum_key in component_settings:
                component_manager.invoke(default_type, 'init',
                                         component_manager,
                                         **(component_settings[default_type.enum_key] or {}),
                                         project_dir=project_dir)
            else:
                component_manager.invoke(
                    default_type, 'init', component_manager, project_dir=project_dir)

    sort_types = DefaultComponentEnums

    # validate config
    ConfigComponentValidator(component_settings)

    if ext_comp_types is not None:
        sort_types = ext_comp_types + sort_types

        # check duplicated key:
        for r_type in sort_types:
            for key in r_type:
                for l_type in sort_types:
                    d_key = None
                    if r_type is not l_type:
                        try:
                            d_key = l_type(key.enum_key)
                        except:
                            continue
                    if d_key is not None:
                        raise KeyError(BaseLocal.get_message(
                            LocalCode_Component_Duplicated_Key, l_type, r_type, key.enum_key))

        if component_settings:
            __create_optional_components(
                component_manager, component_settings, ext_comp_types, project_dir)

    # check componet load failed
    if component_settings:
        for key in component_settings:
            checked = False
            for component in component_manager.components:
                if key == component.component_type.enum_key:
                    checked = True
            if not checked:
                raise ImportError(BaseLocal.get_message(
                    LocalCode_Failed_To_Load_Component, project_dir, key))

    # set with enums order for dispose
    component_manager.set_dispose_components(sort_types)

    return component_manager


def add_module_default_logger(logger_names: List[str]) -> None:
    from .default import LoggerComponent
    LoggerComponent.default_loggers = LoggerComponent.default_loggers + logger_names
