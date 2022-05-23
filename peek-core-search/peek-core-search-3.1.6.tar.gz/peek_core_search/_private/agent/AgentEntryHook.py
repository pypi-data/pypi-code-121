import logging

from peek_core_search.tuples import loadPublicTuples
from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC

logger = logging.getLogger(__name__)


class AgentEntryHook(PluginAgentEntryHookABC):
    def load(self) -> None:
        # Load public tuples so they can be serialised in the agent
        loadPublicTuples()

        logger.debug("Loaded")

    def start(self):
        logger.debug("Started")

    def stop(self):
        logger.debug("Stopped")

    def unload(self):
        logger.debug("Unloaded")
