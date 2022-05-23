import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_eventdb._private.server.controller.AdminStatusController import (
    AdminStatusController,
)

logger = logging.getLogger(__name__)


class AdminStatusTupleProvider(TuplesProviderABC):
    def __init__(self, statusController: AdminStatusController):
        self._statusController = statusController

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        tuples = [self._statusController.status]

        payloadEnvelope = yield Payload(filt, tuples=tuples).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
