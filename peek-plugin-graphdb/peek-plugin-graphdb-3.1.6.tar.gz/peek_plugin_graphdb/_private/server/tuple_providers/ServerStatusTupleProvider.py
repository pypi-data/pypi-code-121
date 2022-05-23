import logging
from typing import Union

from peek_plugin_graphdb._private.server.controller.StatusController import (
    StatusController,
)
from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ServerStatusTupleProvider(TuplesProviderABC):
    def __init__(self, segmentIndexStatus: StatusController):
        self._segmentIndexStatus = segmentIndexStatus

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        tuples = [self._segmentIndexStatus.status]

        payloadEnvelope = yield Payload(filt, tuples=tuples).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
