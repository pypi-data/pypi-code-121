import logging
from typing import Dict

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkUpdateHandlerABC import (
    ACIChunkUpdateHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_core_search._private.client.controller.SearchObjectCacheController import (
    clientSearchObjectUpdateFromServerFilt,
)
from peek_core_search._private.storage.EncodedSearchObjectChunk import (
    EncodedSearchObjectChunk,
)

logger = logging.getLogger(__name__)


class ClientSearchObjectChunkUpdateHandler(ACIChunkUpdateHandlerABC):
    _ChunkedTuple: ACIEncodedChunkTupleABC = EncodedSearchObjectChunk
    _updateFromServerFilt: Dict = clientSearchObjectUpdateFromServerFilt
    _logger: logging.Logger = logger
