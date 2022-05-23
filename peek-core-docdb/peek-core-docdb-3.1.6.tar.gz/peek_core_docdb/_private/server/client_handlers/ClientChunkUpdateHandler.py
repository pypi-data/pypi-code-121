import logging
from typing import Dict

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkUpdateHandlerABC import (
    ACIChunkUpdateHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_core_docdb._private.client.controller.DocumentCacheController import (
    clientDocumentUpdateFromServerFilt,
)
from peek_core_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk

logger = logging.getLogger(__name__)


class ClientChunkUpdateHandler(ACIChunkUpdateHandlerABC):
    _ChunkedTuple: ACIEncodedChunkTupleABC = DocDbEncodedChunk
    _updateFromServerFilt: Dict = clientDocumentUpdateFromServerFilt
    _logger: logging.Logger = logger
