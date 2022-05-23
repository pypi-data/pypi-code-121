from typing import Type

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC

__version__ = '3.1.6'


def peekLogicEntryHook() -> Type[PluginLogicEntryHookABC]:
    from peek_plugin_inbox._private.server.PluginLogicEntryHook import (
        PluginLogicEntryHook,
    )

    return PluginLogicEntryHook


def peekFieldEntryHook() -> Type[PluginClientEntryHookABC]:
    from peek_plugin_inbox._private.client.PluginClientEntryHook import (
        PluginClientEntryHook,
    )

    return PluginClientEntryHook


def peekOfficeEntryHook() -> Type[PluginClientEntryHookABC]:
    from peek_plugin_inbox._private.client.PluginClientEntryHook import (
        PluginClientEntryHook,
    )

    return PluginClientEntryHook
