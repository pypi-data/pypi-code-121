# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

This module defines the base component classes

Modified By: hsky77
Last Updated: May 21st 2022 10:04:13 am
'''


from audioop import reverse
from typing import Dict, Tuple, Any, Union, List
from inspect import iscoroutinefunction

from ...util import DynamicTypeEnum, BaseLocal
from ..constants import LocalCode_Not_Subclass, LocalCode_Component_Type_Not_Exist, Component_Module_Folder


class ComponentTypes(DynamicTypeEnum):
    """base component enum class"""

    @staticmethod
    def get_component_enum_class() -> List[DynamicTypeEnum]:
        try:
            return DynamicTypeEnum.get_dynamic_class_enum_class(Component_Module_Folder)
        except:
            pass

    def import_class(self):
        return super().import_class(cls_type=Component)


class Component():
    """base component class"""

    def __init__(self, component_type: ComponentTypes):
        self.component_type = component_type
        self.component_key = component_type.enum_key

    def init(self, component_manager, *arugs, **kwargs) -> None:
        """called when component_manager create component objects"""
        raise NotImplementedError()

    def info(self) -> Dict:
        """define what meta information of component should be return"""
        return {'component': type(self).__name__, 'info': None}

    def dispose(self, component_manager) -> None:
        pass


class ComponentManager():
    """class to store and manage components"""

    def __init__(self):
        self.__components = {}
        self.__dispose_components = {}

    @property
    def components(self) -> List[Component]:
        return [v for k, v in self.__components.items()]

    @property
    def info(self) -> Dict:
        info = {}
        for component in self.components:
            info[component.component_type.enum_key] = component.info()
        return info

    async def dispose_components(self) -> None:
        for component in self.__dispose_components.values():
            if hasattr(component, 'dispose'):
                func = getattr(component, 'dispose')
                if callable(func):
                    if not iscoroutinefunction(func):
                        func(self)
                    else:
                        await func(self)

    def boardcast(self, method: str, *arugs, **kwargs) -> List[Tuple[ComponentTypes, Any]]:
        """
        this function invokes the non-awaitable methods of stored components and

        return a list of returns from each component methods
        """
        result = []
        for component in self.components:
            if hasattr(component, method):
                func = getattr(component, method)
                if callable(func):
                    if not iscoroutinefunction(func):
                        result.append(
                            (component.component_type, func(*arugs, **kwargs)))
        return result

    async def boardcast_async(self, method: str, *arugs, **kwargs) -> List[Tuple[ComponentTypes, Any]]:
        """
        this function invokes both awaitable and non-awaitable methods of stored components and 

        return a list of returns from each component
        """
        result = []
        for component in self.components:
            if hasattr(component, method):
                func = getattr(component, method)
                if callable(func):
                    if iscoroutinefunction(func):
                        result.append((component.component_type, await func(*arugs, **kwargs)))
                    else:
                        result.append(
                            (component.component_type, func(*arugs, **kwargs)))
        return result

    def invoke(self, enum_type: Union[str, ComponentTypes], method: str, *arugs, **kwargs) -> Any:
        """execute component mehtod by giving the method name and arguments"""
        component = self.get_component(enum_type)
        func = getattr(component, method, None)
        if callable(func):
            if not iscoroutinefunction(func):
                return func(*arugs, **kwargs)

    async def invoke_async(self, enum_type: Union[str, ComponentTypes], method: str, *arugs, **kwargs) -> Any:
        """asynchronously execute component mehtod by giving the method name and arguments"""
        component = self.get_component(enum_type)
        func = getattr(component, method, None)
        if callable(func):
            if iscoroutinefunction(func):
                return await func(*arugs, **kwargs)

    def set_component(self, component: Component) -> None:
        """add or replace component object"""
        if isinstance(component, Component):
            self.__components[component.component_key] = component
        else:
            raise TypeError(BaseLocal.get_message(
                LocalCode_Not_Subclass, type(component), Component))

    def get_component(self, enum_type: Union[str, ComponentTypes]) -> Component:
        """return stored component object"""
        key = self.__get_component_key(enum_type)
        if key in self.__components:
            return self.__components[key]

        raise KeyError(BaseLocal.get_message(
            LocalCode_Component_Type_Not_Exist, enum_type))

    def has_component(self, enum_type: Union[str, ComponentTypes]) -> bool:
        return self.__get_component_key(enum_type) in self.__components

    def set_dispose_components(self, order_list: List[ComponentTypes]):
        """
        sort component object by "order_list". default sorting with ComponentTypes order

        notes: considering the component dependencies, use ComponentTypes enum class to make the order to dispose components when server shut down
        """
        orders = []
        for x in order_list:
            reverse_array = [k for k in reversed([y.enum_key for y in x])]
            if reverse_array is not None:
                orders = orders + reverse_array
        self.__dispose_components = {
            x: self.__components[x] for x in orders if x in self.__components}

    def __get_component_key(self, enum_type: Union[str, ComponentTypes]) -> str:
        if isinstance(enum_type, ComponentTypes):
            return enum_type.enum_key
        return enum_type
