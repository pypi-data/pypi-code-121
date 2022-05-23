import logging

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_core_docdb._private.PluginNames import docDbFilt
from peek_core_docdb._private.server.client_handlers.ClientChunkLoadRpc import (
    ClientChunkLoadRpc,
)
from peek_core_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk

logger = logging.getLogger(__name__)

clientDocumentUpdateFromServerFilt = dict(key="clientDocumentUpdateFromServer")
clientDocumentUpdateFromServerFilt.update(docDbFilt)


class DocumentCacheController(ACICacheControllerABC):
    """Document Cache Controller

    The Document cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _ChunkedTuple = DocDbEncodedChunk
    _chunkLoadRpcMethod = ClientChunkLoadRpc.loadDocumentChunks
    _updateFromServerFilt = clientDocumentUpdateFromServerFilt
    _logger = logger
