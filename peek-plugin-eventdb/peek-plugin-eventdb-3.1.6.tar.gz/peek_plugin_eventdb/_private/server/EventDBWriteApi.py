import logging
from typing import List

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_eventdb._private.server.EventDBReadApi import EventDBReadApi
from peek_plugin_eventdb._private.server.controller.EventDBController import (
    EventDBController,
)
from peek_plugin_eventdb._private.server.controller.EventDBImportController import (
    EventDBImportController,
)
from peek_plugin_eventdb.server.EventDBWriteApiABC import EventDBWriteApiABC

logger = logging.getLogger(__name__)


class EventDBWriteApi(EventDBWriteApiABC):
    def __init__(self):
        self._queueController = None
        self._eventdbController = None
        self._eventdbImportController = None
        self._readApi = None
        self._dbSessionCreator = None
        self._dbEngine = None

    def setup(
        self,
        eventdbController: EventDBController,
        eventdbImportController: EventDBImportController,
        readApi: EventDBReadApi,
        dbSessionCreator,
        dbEngine,
    ):
        self._eventdbController = eventdbController
        self._eventdbImportController = eventdbImportController
        self._readApi = readApi
        self._dbSessionCreator = dbSessionCreator
        self._dbEngine = dbEngine

    def shutdown(self):
        pass

    @inlineCallbacks
    def addEvents(self, modelSetKey: str, eventsEncodedPayload: str) -> Deferred:
        if not eventsEncodedPayload:
            return

        yield self._eventdbImportController.importEvents(
            modelSetKey, eventsEncodedPayload
        )

    @inlineCallbacks
    def removeEvents(self, modelSetKey: str, eventKeys: List[str]) -> Deferred:
        if not eventKeys:
            return

        yield self._eventdbImportController.deleteEvents(modelSetKey, eventKeys)

    @inlineCallbacks
    def updateAlarmFlags(
        self, modelSetKey: str, eventKeys: List[str], alarmFlag: bool
    ) -> Deferred:
        if not eventKeys:
            return

        yield self._eventdbImportController.updateAlarmFlags(
            modelSetKey, eventKeys, alarmFlag
        )

    @inlineCallbacks
    def replaceProperties(
        self, modelSetKey: str, propertiesEncodedPayload: str
    ) -> Deferred:
        if not propertiesEncodedPayload:
            return

        yield self._eventdbImportController.replaceProperties(
            modelSetKey, propertiesEncodedPayload
        )
