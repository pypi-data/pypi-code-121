from typing import Type

from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC

__version__ = '3.1.6'


def peekFieldEntryHook() -> Type[PluginClientEntryHookABC]:
    from peek_core_user._private.client.PluginClientEntryHook import (
        PluginClientEntryHook,
    )

    return PluginClientEntryHook


def peekOfficeEntryHook() -> Type[PluginClientEntryHookABC]:
    from peek_core_user._private.client.PluginClientEntryHook import (
        PluginClientEntryHook,
    )

    return PluginClientEntryHook


def peekAgentEntryHook() -> Type[PluginAgentEntryHookABC]:
    from ._private.agent.AgentEntryHook import AgentEntryHook

    return AgentEntryHook


def peekLogicEntryHook() -> Type[PluginLogicEntryHookABC]:
    from peek_core_user._private.server.PluginLogicEntryHook import PluginLogicEntryHook

    return PluginLogicEntryHook


def peekWorkerEntryHook() -> Type[PluginWorkerEntryHookABC]:
    from ._private.worker.WorkerEntryHook import WorkerEntryHook

    return WorkerEntryHook
