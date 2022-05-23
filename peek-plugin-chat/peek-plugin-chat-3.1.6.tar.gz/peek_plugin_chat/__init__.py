__version__ = '3.1.6'

from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from typing import Type

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC


def peekOfficeEntryHook() -> Type[PluginClientEntryHookABC]:
    from ._private.client.ClientEntryHook import ClientEntryHook

    return ClientEntryHook


def peekFieldEntryHook() -> Type[PluginClientEntryHookABC]:
    from ._private.client.ClientEntryHook import ClientEntryHook

    return ClientEntryHook


def peekLogicEntryHook() -> Type[PluginLogicEntryHookABC]:
    from ._private.server.LogicEntryHook import LogicEntryHook

    return LogicEntryHook
