import logging
import time

from peek_plugin_diagram._private.worker.tasks.ImportDispTask import importDispsTask
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class DispImportController:
    def __init__(self, liveDbWriteApi: LiveDBWriteApiABC):
        self._liveDbWriteApi = liveDbWriteApi

    def shutdown(self):
        self._liveDbWriteApi = None

    @inlineCallbacks
    def importDisps(
        self,
        modelSetKey: str,
        coordSetKey: str,
        importGroupHash: str,
        dispsEncodedPayload: bytes,
    ):
        liveDbItemsToImport = yield importDispsTask.delay(
            modelSetKey, coordSetKey, importGroupHash, dispsEncodedPayload
        )

        if liveDbItemsToImport:
            yield self._liveDbWriteApi.importLiveDbItems(
                modelSetKey, liveDbItemsToImport
            )

            # Give and connector plugins time to load the new items
            yield self._sleep(2.0)

            yield self._liveDbWriteApi.pollLiveDbValueAcquisition(
                modelSetKey, [i.key for i in liveDbItemsToImport]
            )

    def _sleep(self, seconds):
        d = Deferred()
        reactor.callLater(seconds, d.callback, True)
        return d
