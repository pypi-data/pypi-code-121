# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: August 27th 2020 12:26:00 pm
'''


from enum import Enum
from typing import Callable, Any, Union, Tuple
from threading import get_ident
from inspect import iscoroutinefunction

from . import BaseLocal
from .constants import LocalCode_Not_Valid_Enum, LocalCode_Not_ASYNC_FUNC, LocalCode_Invalid_Thread_Safe_Call


class Callbacks():
    """
    Enum managed callback functions. Basically, this is useful to communicate between the controller instances.
    """

    def __init__(self, callback_enum_cls: Enum, thread_safe: bool = True):
        self.callbacks = {}
        self.callback_type_cls = callback_enum_cls
        self.thread_safe = thread_safe

    def add_callback(self, callback_enum: Enum, callback: Callable) -> None:
        """
        Register callback function with the given enum
        """
        callback_type = self.callback_type_cls(callback_enum)

        if callable(callback):
            if not callback_type in self.callbacks:
                self.callbacks[callback_type] = []

            self.callbacks[callback_type].append(self.__make_item(callback))

    def remove_callback(self, callback_enum: Enum, callback: Callable) -> None:
        """
        Unregister callback function with the given enum
        """
        callback_type = self.callback_type_cls(callback_enum)

        if callback_type in self.callbacks:
            self.callbacks[callback_type].remove(self.__make_item(callback))

    def execute_callback(self, callback_enum: Enum, *arugs, **kwargs) -> None:
        """
        Execute synchronizing callback functions with the given enum
        """
        callback_enum = self.__get_valid_enum(callback_enum)

        thread_id = get_ident
        for cb in self.callbacks[callback_enum]:
            if self.thread_safe and not cb[0] == thread_id:
                raise RuntimeError(BaseLocal.get_message(
                    LocalCode_Invalid_Thread_Safe_Call, thread_id, cb[0]))

            cb[1](*arugs, **kwargs)

    async def execute_callback_async(self, callback_enum: Union[Enum, str], *arugs, **kwargs) -> None:
        """
        Execute asynchronizing callback functions with the given enum
        """
        callback_enum = self.__get_valid_enum(callback_enum)

        thread_id = get_ident
        for cb in self.callbacks[callback_enum]:
            if self.thread_safe and not cb[0] == thread_id:
                raise RuntimeError(BaseLocal.get_message(
                    LocalCode_Invalid_Thread_Safe_Call, thread_id, cb[0]))

            if iscoroutinefunction(cb[1]):
                await cb[1](*arugs, **kwargs)
            else:
                raise TypeError(BaseLocal.get_message(
                    LocalCode_Not_ASYNC_FUNC, cb[1].__name__))

    def __make_item(self, callback: Callable) -> Tuple:
        return (get_ident, callback)

    def __get_valid_enum(self, callback_enum: Enum) -> Enum:
        callback_type = self.callback_type_cls(callback_enum)

        if not callback_type in self.callbacks:
            raise TypeError(BaseLocal.get_message(
                LocalCode_Not_Valid_Enum, callback_enum, self.callback_type_cls))

        return callback_type
