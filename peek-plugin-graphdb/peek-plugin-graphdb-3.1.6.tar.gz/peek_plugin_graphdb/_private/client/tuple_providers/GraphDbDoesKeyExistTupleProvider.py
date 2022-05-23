import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import (
    ItemKeyIndexCacheController,
)
from peek_plugin_graphdb.tuples.GraphDbDoesKeyExistTuple import GraphDbDoesKeyExistTuple

logger = logging.getLogger(__name__)


class GraphDbDoesKeyExistTupleProvider(TuplesProviderABC):
    def __init__(self, itemKeyCacheController: ItemKeyIndexCacheController):
        self._itemKeyCacheController = itemKeyCacheController

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        vertexOrEdgeKey = tupleSelector.selector["vertexOrEdgeKey"]

        doesItExist = yield self._itemKeyCacheController.doesKeyExist(
            modelSetKey, vertexOrEdgeKey
        )

        tuple_ = GraphDbDoesKeyExistTuple(exists=doesItExist)

        envelope = yield Payload(filt, tuples=[tuple_]).makePayloadEnvelopeDefer()
        vortexMsg = yield envelope.toVortexMsgDefer()
        return vortexMsg
