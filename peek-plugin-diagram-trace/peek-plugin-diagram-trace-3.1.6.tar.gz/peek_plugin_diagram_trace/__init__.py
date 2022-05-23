from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from typing import Type

__version__ = '3.1.6'


def peekLogicEntryHook() -> Type[PluginLogicEntryHookABC]:
    from ._private.server.LogicEntryHook import LogicEntryHook

    return LogicEntryHook


def peekOfficeEntryHook() -> Type[PluginClientEntryHookABC]:
    from ._private.client.ClientEntryHook import ClientEntryHook

    return ClientEntryHook


def peekFieldEntryHook() -> Type[PluginClientEntryHookABC]:
    from ._private.client.ClientEntryHook import ClientEntryHook

    return ClientEntryHook
