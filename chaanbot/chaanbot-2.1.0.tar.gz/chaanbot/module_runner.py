import logging
import time

from nio import MatrixRoom, RoomMessage

logger = logging.getLogger("module_runner")

""" Responsible for running modules on messages in rooms """


class ModuleRunner:
    MAX_AGE_OF_EVENT_TO_BE_NEW_SECONDS = 30 * 60  # Events older than 30 minutes can be ignored

    def __init__(self, config, matrix, module_loader):
        try:
            self.loaded_modules = module_loader.load_modules(config, matrix)
        except IOError as e:
            logger.warning("Could not load module(s) due to: {}".format(str(e)), e)

    async def run(self, event: RoomMessage, room: MatrixRoom, message):
        logger.debug("Running {} modules on message".format(len(self.loaded_modules)))
        if self._is_old_event(event):
            logger.warning("Event is too old, discard it. This should happen very rarely")
        else:
            for module in self.loaded_modules:
                await module.run(room, event, message)

    def _is_old_event(self, event: RoomMessage):
        return (time.time() - (event.server_timestamp / 1000)) > self.MAX_AGE_OF_EVENT_TO_BE_NEW_SECONDS
