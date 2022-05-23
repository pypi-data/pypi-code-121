import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import EncodedGridTuple
from twisted.internet.defer import DeferredList, Deferred, inlineCallbacks
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.client.controller.GridCacheController import (
    GridCacheController,
)
from peek_plugin_diagram._private.server.client_handlers.ClientGridLoaderRpc import (
    ClientGridLoaderRpc,
)
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndexCompiled

logger = logging.getLogger(__name__)

clientGridWatchUpdateFromDeviceFilt = {"key": "clientGridWatchUpdateFromDevice"}
clientGridWatchUpdateFromDeviceFilt.update(diagramFilt)

#: This the type of the data that we get when the clients observe new grids.
DeviceGridT = Dict[str, datetime]


# ModelSet HANDLER
class GridCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = GridKeyIndexCompiled
    _updateFromServerFilt: Dict = clientGridWatchUpdateFromDeviceFilt
    _logger: logging.Logger = logger

    def __init__(self, cacheController: GridCacheController, clientId: str):
        """App Grid Handler

        This class handles the custom needs of the desktop/mobile apps observing grids.

        """
        ACICacheHandlerABC.__init__(self, cacheController, clientId)

        # We need to know who is watching what so we can tell the server.
        self._observedGridKeysByVortexUuid = defaultdict(list)
        self._observedVortexUuidsByGridKey = defaultdict(list)

        # We're not using this
        del self._uuidsObserving

    # ---------------
    # Filter out offline vortexes

    def _filterOutOfflineVortexes(self):
        # TODO, Change this to observe offline vortexes
        # This depends on the VortexFactory offline observable implementation.
        # Which is incomplete at this point :-|

        vortexUuids = set(VortexFactory.getRemoteVortexUuids())
        vortexUuidsToRemove = set(self._observedGridKeysByVortexUuid) - vortexUuids

        if not vortexUuidsToRemove:
            return

        for vortexUuid in vortexUuidsToRemove:
            del self._observedGridKeysByVortexUuid[vortexUuid]

        self._rebuildStructs()

    # ---------------
    # Process update from the server

    def notifyOfUpdate(self, gridKeys: List[str]):
        """Notify of Grid Updates

        This method is called by the client.GridCacheController when it receives updates
        from the server.

        """
        self._filterOutOfflineVortexes()

        payloadsByVortexUuid = defaultdict(Payload)

        for gridKey in gridKeys:

            gridTuple = self._cacheController.encodedChunk(gridKey)
            if not gridTuple:
                gridTuple = EncodedGridTuple()
                gridTuple.gridKey = gridKeys

            vortexUuids = self._observedVortexUuidsByGridKey.get(gridKey, [])

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug(
                    "Sending unsolicited grid %s to vortex %s", gridKey, vortexUuid
                )
                payloadsByVortexUuid[vortexUuid].tuples.append(gridTuple)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientGridWatchUpdateFromDeviceFilt

            # Serliase in thread, and then send.
            d = payload.makePayloadEnvelopeDefer()
            d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
            d.addCallback(VortexFactory.sendVortexMsg, destVortexUuid=vortexUuid)
            dl.append(d)

        # Log the errors, otherwise we don't care about them
        dl = DeferredList(dl, fireOnOneErrback=True)
        dl.addErrback(vortexLogFailure, logger, consumeError=True)

    # ---------------
    # Process observes from the devices

    @inlineCallbacks
    def _processObserve(
        self,
        payloadEnvelope: PayloadEnvelope,
        vortexUuid: str,
        sendResponse: SendVortexMsgResponseCallable,
        **kwargs
    ):
        cacheAll = payloadEnvelope.filt.get("cacheAll") == True

        payload = yield payloadEnvelope.decodePayloadDefer()

        lastUpdateByGridKey: DeviceGridT = payload.tuples[0]

        if not cacheAll:
            gridKeys = list(lastUpdateByGridKey.keys())
            self._observedGridKeysByVortexUuid[vortexUuid] = gridKeys
            self._rebuildStructs()

        self._replyToObserve(
            payload.filt, lastUpdateByGridKey, sendResponse, cacheAll=cacheAll
        )

    def _rebuildStructs(self) -> None:
        """Rebuild Structs

        Rebuild the reverse index of uuids by grid key.

        :returns: None
        """
        # Rebuild the other reverse lookup
        newDict = defaultdict(list)

        for vortexUuid, gridKeys in self._observedGridKeysByVortexUuid.items():
            for gridKey in gridKeys:
                newDict[gridKey].append(vortexUuid)

        keysChanged = set(self._observedVortexUuidsByGridKey) != set(newDict)

        self._observedVortexUuidsByGridKey = newDict

        # Notify the server that this client service is watching different grids.
        if keysChanged:
            d = ClientGridLoaderRpc.updateClientWatchedGrids(
                clientId=self._clientId,
                gridKeys=list(self._observedVortexUuidsByGridKey),
            )
            d.addErrback(vortexLogFailure, logger, consumeError=False)

    # ---------------
    # Reply to device observe

    def _replyToObserve(
        self,
        filt,
        lastUpdateByGridKey: DeviceGridT,
        sendResponse: SendVortexMsgResponseCallable,
        cacheAll=False,
    ) -> None:
        """Reply to Observe

        The client has told us that it's observing a new set of grids, and the lastUpdate
        it has for each of those grids. We will send them the grids that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByGridKey: The dict of gridKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        gridTuplesToSend = []

        def sendChunk(toSend):
            if not toSend and not cacheAll:
                return

            payload = Payload(filt=filt, tuples=toSend)
            d: Deferred = payload.makePayloadEnvelopeDefer(compressionLevel=2)
            d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
            d.addCallback(sendResponse)
            d.addErrback(vortexLogFailure, logger, consumeError=True)

        # Check and send any updates
        for gridKey, lastUpdate in lastUpdateByGridKey.items():
            # NOTE: lastUpdate can be null.
            gridTuple = self._cacheController.encodedChunk(gridKey)

            # Last update is not null, we need to send an empty grid.
            if not gridTuple:
                gridTuple = EncodedGridTuple()
                gridTuple.gridKey = gridKey
                gridTuple.lastUpdate = lastUpdate
                gridTuple.encodedGridTuple = None
                gridTuplesToSend.append(gridTuple)
                logger.debug(
                    "Grid %s is no loner in the cache, %s", gridKey, lastUpdate
                )

            elif gridTuple.lastUpdate == lastUpdate:
                logger.debug("Grid %s matches the cache, %s", gridKey, lastUpdate)

            else:
                gridTuplesToSend.append(gridTuple)
                logger.debug("Sending grid %s from the cache, %s", gridKey, lastUpdate)

            if len(gridTuplesToSend) == 5 and not cacheAll:
                sendChunk(gridTuplesToSend)
                gridTuplesToSend = []

        sendChunk(gridTuplesToSend)
