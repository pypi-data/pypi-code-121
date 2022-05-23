from peek_plugin_eventdb._private.server.EventDBReadApi import EventDBReadApi
from peek_plugin_eventdb._private.server.EventDBWriteApi import EventDBWriteApi
from peek_plugin_eventdb._private.server.controller.EventDBController import (
    EventDBController,
)
from peek_plugin_eventdb._private.server.controller.EventDBImportController import (
    EventDBImportController,
)
from peek_plugin_eventdb.server.EventDBApiABC import EventDBApiABC
from peek_plugin_eventdb.server.EventDBReadApiABC import EventDBReadApiABC
from peek_plugin_eventdb.server.EventDBWriteApiABC import EventDBWriteApiABC


class EventDBApi(EventDBApiABC):
    def __init__(self):
        self._readApi = EventDBReadApi()
        self._writeApi = EventDBWriteApi()

    def setup(
        self,
        eventdbController: EventDBController,
        eventdbImportController: EventDBImportController,
        dbSessionCreator,
        dbEngine,
    ):
        self._readApi.setup(
            eventdbController=eventdbController,
            dbSessionCreator=dbSessionCreator,
            dbEngine=dbEngine,
        )

        self._writeApi.setup(
            eventdbController=eventdbController,
            eventdbImportController=eventdbImportController,
            readApi=self._readApi,
            dbSessionCreator=dbSessionCreator,
            dbEngine=dbEngine,
        )

    def shutdown(self):
        self._readApi.shutdown()
        self._writeApi.shutdown()

        self._readApi = None
        self._writeApi = None

    @property
    def writeApi(self) -> EventDBWriteApiABC:
        return self._writeApi

    @property
    def readApi(self) -> EventDBReadApiABC:
        return self._readApi
