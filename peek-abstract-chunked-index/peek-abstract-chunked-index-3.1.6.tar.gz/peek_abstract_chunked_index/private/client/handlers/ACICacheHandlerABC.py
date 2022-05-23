import logging
from abc import ABCMeta
from collections import defaultdict
from typing import List, Dict

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)

# ModelSet HANDLER
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)


class ACICacheHandlerABC(metaclass=ABCMeta):
    _UpdateDateTuple: ACIUpdateDateTupleABC = None
    _updateFromServerFilt: Dict = None
    _logger: logging.Logger = None

    def __init__(self, cacheController: ACICacheControllerABC, clientId: str):
        """App ChunkedIndex Handler

        This class handles the custom needs of the desktop/mobile apps observing chunkedIndexs.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            self._updateFromServerFilt, self._processObserve
        )

        self._uuidsObserving = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfUpdate(self, chunkKeys: List[str]):
        """Notify of ChunkedIndex Updates

        This method is called by the client.ChunkedIndexCacheController when it receives updates
        from the server.

        """
        vortexUuids = set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        self._uuidsObserving = vortexUuids

        payloadsByVortexUuid = defaultdict(Payload)

        for chunkKey in chunkKeys:
            encodedChunkedIndexChunk = self._cacheController.encodedChunk(chunkKey)

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                self._logger.debug(
                    "Sending unsolicited chunkedIndex %s to vortex %s",
                    chunkKey,
                    vortexUuid,
                )
                payloadsByVortexUuid[vortexUuid].tuples.append(encodedChunkedIndexChunk)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = self._updateFromServerFilt

            # Serialise in thread, and then send.
            d = payload.makePayloadEnvelopeDefer()
            d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
            d.addCallback(VortexFactory.sendVortexMsg, destVortexUuid=vortexUuid)
            dl.append(d)

        # Log the errors, otherwise we don't care about them
        dl = DeferredList(dl, fireOnOneErrback=True)
        dl.addErrback(vortexLogFailure, self._logger, consumeError=True)

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

        payload = yield payloadEnvelope.decodePayloadDefer()

        updateDatesTuples: ACIUpdateDateTupleABC = payload.tuples[0]

        self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(
            payload.filt,
            updateDatesTuples.ckiUpdateDateByChunkKey,
            sendResponse,
            vortexUuid,
        )

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(
        self,
        filt,
        lastUpdateByChunkedIndexKey: Dict[str, str],
        sendResponse: SendVortexMsgResponseCallable,
        vortexUuid: str,
    ) -> None:
        """Reply to Observe

        The client has told us that it's observing a new set of chunkedIndexs, and the lastUpdate
        it has for each of those chunkedIndexs. We will send them the chunkedIndexs that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByChunkedIndexKey: The dict of chunkedIndexKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        chunkedIndexTuplesToSend = []

        # Check and send any updates
        for chunkedIndexKey, lastUpdate in lastUpdateByChunkedIndexKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                self._logger.debug("Vortex %s is offline, stopping update")
                return

            # NOTE: lastUpdate can be null.
            encodedChunkedIndexTuple = self._cacheController.encodedChunk(
                chunkedIndexKey
            )
            if not encodedChunkedIndexTuple:
                self._logger.debug(
                    "ChunkedIndex %s is not in the cache" % chunkedIndexKey
                )
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            self._logger.debug(
                "%s, %s,  %s",
                encodedChunkedIndexTuple.ckiLastUpdate == lastUpdate,
                encodedChunkedIndexTuple.ckiLastUpdate,
                lastUpdate,
            )

            if encodedChunkedIndexTuple.ckiLastUpdate == lastUpdate:
                self._logger.debug(
                    "ChunkedIndex %s matches the cache" % chunkedIndexKey
                )
                continue

            chunkedIndexTuplesToSend.append(encodedChunkedIndexTuple)
            self._logger.debug(
                "Sending chunkedIndex %s from the cache" % chunkedIndexKey
            )

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=chunkedIndexTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, self._logger, consumeError=True)
