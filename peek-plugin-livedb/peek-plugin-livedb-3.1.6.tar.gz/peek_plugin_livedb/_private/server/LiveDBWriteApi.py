import logging
from typing import List

from twisted.internet import defer
from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_livedb._private.server.LiveDBReadApi import LiveDBReadApi
from peek_plugin_livedb._private.server.controller.LiveDbController import (
    LiveDbController,
)
from peek_plugin_livedb._private.server.controller.LiveDbImportController import (
    LiveDbImportController,
)
from peek_plugin_livedb._private.server.controller.LiveDbValueUpdateQueueController import (
    LiveDbValueUpdateQueueController,
)
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC
from peek_plugin_livedb.tuples.ImportLiveDbItemTuple import ImportLiveDbItemTuple
from peek_plugin_livedb.tuples.LiveDbRawValueUpdateTuple import (
    LiveDbRawValueUpdateTuple,
)

logger = logging.getLogger(__name__)


class LiveDBWriteApi(LiveDBWriteApiABC):
    def __init__(self):
        self._queueController = None
        self._liveDbController = None
        self._liveDbImportController = None
        self._readApi = None
        self._dbSessionCreator = None
        self._dbEngine = None

    def setup(
        self,
        queueController: LiveDbValueUpdateQueueController,
        liveDbController: LiveDbController,
        liveDbImportController: LiveDbImportController,
        readApi: LiveDBReadApi,
        dbSessionCreator,
        dbEngine,
    ):
        self._queueController = queueController
        self._liveDbController = liveDbController
        self._liveDbImportController = liveDbImportController
        self._readApi = readApi
        self._dbSessionCreator = dbSessionCreator
        self._dbEngine = dbEngine

    def shutdown(self):
        pass

    @inlineCallbacks
    def updateRawValues(
        self, modelSetName: str, updates: List[LiveDbRawValueUpdateTuple]
    ) -> Deferred:
        """Update Raw Values"""
        if not updates:
            return

        yield self._queueController.queueData(modelSetName, updates)

        self._readApi.rawValueUpdatesObservable(modelSetName).on_next(updates)

    def importLiveDbItems(
        self, modelSetName: str, newItems: List[ImportLiveDbItemTuple]
    ) -> Deferred:
        if not newItems:
            return defer.succeed(True)

        return self._liveDbImportController.importLiveDbItems(modelSetName, newItems)

    def prioritiseLiveDbValueAcquisition(
        self, modelSetName: str, liveDbKeys: List[str]
    ) -> Deferred:
        self._readApi.priorityKeysObservable(modelSetName).on_next(liveDbKeys)
        return defer.succeed(True)

    def pollLiveDbValueAcquisition(
        self, modelSetName: str, liveDbKeys: List[str]
    ) -> Deferred:
        self._readApi.pollKeysObservable(modelSetName).on_next(liveDbKeys)
        return defer.succeed(True)
