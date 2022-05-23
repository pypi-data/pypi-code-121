from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
from typing import Type

__version__ = '3.1.6'


def peekLogicEntryHook() -> Type[PluginLogicEntryHookABC]:
    from .private.server.LogicEntryHook import LogicEntryHook

    return LogicEntryHook


def peekAgentEntryHook() -> Type[PluginAgentEntryHookABC]:
    from .private.agent.AgentEntryHook import AgentEntryHook

    return AgentEntryHook
