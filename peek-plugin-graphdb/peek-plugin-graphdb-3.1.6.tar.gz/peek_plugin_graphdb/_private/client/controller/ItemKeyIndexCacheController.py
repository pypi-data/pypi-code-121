import json
import logging
from typing import List

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.server.client_handlers.ItemKeyIndexChunkLoadRpc import (
    ItemKeyIndexChunkLoadRpc,
)
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import (
    ItemKeyIndexEncodedChunk,
)
from peek_plugin_graphdb._private.worker.tasks._ItemKeyIndexCalcChunkKey import (
    makeChunkKeyForItemKey,
)
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload

logger = logging.getLogger(__name__)

clientItemKeyIndexUpdateFromServerFilt = dict(key="clientItemKeyIndexUpdateFromServer")
clientItemKeyIndexUpdateFromServerFilt.update(graphDbFilt)


class ItemKeyIndexCacheController(ACICacheControllerABC):
    """ItemKeyIndex Cache Controller

    The ItemKeyIndex cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _ChunkedTuple = ItemKeyIndexEncodedChunk
    _chunkLoadRpcMethod = ItemKeyIndexChunkLoadRpc.loadItemKeyIndexChunks
    _updateFromServerFilt = clientItemKeyIndexUpdateFromServerFilt
    _logger = logger

    def getSegmentKeys(self, modelSetKey: str, vertexKey: str) -> List[str]:

        chunkKey = makeChunkKeyForItemKey(modelSetKey, vertexKey)
        # noinspection PyTypeChecker
        chunk: ItemKeyIndexEncodedChunk = self.encodedChunk(chunkKey)

        if not chunk:
            logger.warning("ItemKeyIndex chunk %s is missing from cache", chunkKey)
            return []

        resultsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
        resultsByKey = json.loads(resultsByKeyStr)

        if vertexKey not in resultsByKey:
            logger.warning(
                "ItemKey %s is missing from index, chunkKey %s", vertexKey, chunkKey
            )
            return []

        packedJson = resultsByKey[vertexKey]

        segmentKeys = json.loads(packedJson)

        return segmentKeys

    @deferToThreadWrapWithLogger(logger)
    def doesKeyExist(self, modelSetKey: str, vertexOrEdgeKey: str) -> bool:

        chunkKey = makeChunkKeyForItemKey(modelSetKey, vertexOrEdgeKey)
        # noinspection PyTypeChecker
        chunk: ItemKeyIndexEncodedChunk = self.encodedChunk(chunkKey)

        if not chunk:
            return False

        resultsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
        resultsByKey = json.loads(resultsByKeyStr)

        return vertexOrEdgeKey in resultsByKey
