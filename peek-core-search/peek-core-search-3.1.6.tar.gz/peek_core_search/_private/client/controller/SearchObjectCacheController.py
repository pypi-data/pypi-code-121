import logging
from collections import defaultdict
from typing import List, Optional

import json
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.server.client_handlers.ClientChunkLoadRpc import (
    ClientChunkLoadRpc,
)
from peek_core_search._private.storage.EncodedSearchObjectChunk import (
    EncodedSearchObjectChunk,
)
from peek_core_search._private.storage.SearchObjectTypeTuple import (
    SearchObjectTypeTuple,
)
from peek_core_search._private.tuples.search_object.SearchResultObjectRouteTuple import (
    SearchResultObjectRouteTuple,
)
from peek_core_search._private.tuples.search_object.SearchResultObjectTuple import (
    SearchResultObjectTuple,
)
from peek_core_search._private.worker.tasks._CalcChunkKey import (
    makeSearchObjectChunkKey,
)

logger = logging.getLogger(__name__)

clientSearchObjectUpdateFromServerFilt = dict(key="clientSearchObjectUpdateFromServer")
clientSearchObjectUpdateFromServerFilt.update(searchFilt)


class SearchObjectCacheController(ACICacheControllerABC):
    """SearchObject Cache Controller

    The SearchObject cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _ChunkedTuple = EncodedSearchObjectChunk
    _chunkLoadRpcMethod = ClientChunkLoadRpc.loadSearchObjectChunks
    _updateFromServerFilt = clientSearchObjectUpdateFromServerFilt
    _logger = logger

    @deferToThreadWrapWithLogger(logger)
    def getObjects(
        self, objectTypeId: Optional[int], objectIds: List[int]
    ) -> List[SearchResultObjectTuple]:
        return self.getObjectsBlocking(objectTypeId, objectIds)

    def getObjectsBlocking(
        self, objectTypeId: Optional[int], objectIds: List[int]
    ) -> List[SearchResultObjectTuple]:

        objectIdsByChunkKey = defaultdict(list)
        for objectId in objectIds:
            objectIdsByChunkKey[makeSearchObjectChunkKey(objectId)].append(objectId)

        foundObjects: List[SearchResultObjectTuple] = []
        for chunkKey, subObjectIds in objectIdsByChunkKey.items():
            foundObjects += self._getObjectsForChunkBlocking(
                chunkKey, objectTypeId, subObjectIds
            )

        return foundObjects

    def _getObjectsForChunkBlocking(
        self, chunkKey: str, objectTypeId: Optional[int], objectIds: List[int]
    ) -> List[SearchResultObjectTuple]:

        chunk = self.encodedChunk(chunkKey)
        if not chunk:
            return []

        objectPropsByIdStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
        objectPropsById = json.loads(objectPropsByIdStr)

        foundObjects: List[SearchResultObjectTuple] = []

        for objectId in objectIds:
            if str(objectId) not in objectPropsById:
                logger.warning(
                    "Search object id %s is missing from index, chunkKey %s",
                    objectId,
                    chunkKey,
                )
                continue

            # Reconstruct the data
            objectProps: {} = json.loads(objectPropsById[str(objectId)])

            # Get out the object type
            thisObjectTypeId = objectProps["_otid_"]
            del objectProps["_otid_"]

            # If the property is set, then make sure it matches
            if objectTypeId is not None and objectTypeId != thisObjectTypeId:
                continue

            # Get out the routes
            routes: List[List[str]] = objectProps["_r_"]
            del objectProps["_r_"]

            # Get the key
            objectKey: str = objectProps["key"]

            # Create the new object
            newObject = SearchResultObjectTuple()
            foundObjects.append(newObject)

            newObject.id = objectId
            newObject.key = objectKey
            newObject.objectType = SearchObjectTypeTuple(id=thisObjectTypeId)
            newObject.properties = objectProps

            for route in routes:
                newRoute = SearchResultObjectRouteTuple()
                newObject.routes.append(newRoute)

                newRoute.title = route[0]
                newRoute.path = route[1]

        return foundObjects
