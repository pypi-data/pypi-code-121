import logging
from typing import List, Any

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.server.client_handlers.ClientChunkLoadRpc import (
    ClientChunkLoadRpc,
)
from peek_core_search._private.storage.EncodedSearchIndexChunk import (
    EncodedSearchIndexChunk,
)

logger = logging.getLogger(__name__)

clientSearchIndexUpdateFromServerFilt = dict(key="clientSearchIndexUpdateFromServer")
clientSearchIndexUpdateFromServerFilt.update(searchFilt)


class SearchIndexCacheController(ACICacheControllerABC):
    """SearchIndex Cache Controller

    The SearchIndex cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _ChunkedTuple = EncodedSearchIndexChunk
    _chunkLoadRpcMethod = ClientChunkLoadRpc.loadSearchIndexChunks
    _updateFromServerFilt = clientSearchIndexUpdateFromServerFilt
    _logger = logger

    def __init__(self, clientId: str):
        ACICacheControllerABC.__init__(self, clientId)
        self._fastKeywordController = None

    def setFastKeywordController(self, fastKeywordController):
        self._fastKeywordController = fastKeywordController

    def shutdown(self):
        ACICacheControllerABC.shutdown(self)
        self._fastKeywordController = None

    def _notifyOfChunkKeysUpdated(self, chunkKeys: List[Any]):
        ACICacheControllerABC._notifyOfChunkKeysUpdated(self, chunkKeys)
        self._fastKeywordController.notifyOfUpdate(chunkKeys)
