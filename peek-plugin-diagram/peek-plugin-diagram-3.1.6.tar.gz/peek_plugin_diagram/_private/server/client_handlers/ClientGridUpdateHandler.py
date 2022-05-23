import logging
from typing import Dict

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkUpdateHandlerABC import (
    ACIChunkUpdateHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_diagram._private.client.controller.GridCacheController import (
    clientGridUpdateFromServerFilt,
)
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndexCompiled

logger = logging.getLogger(__name__)


class ClientGridUpdateHandler(ACIChunkUpdateHandlerABC):
    _ChunkedTuple: ACIEncodedChunkTupleABC = GridKeyIndexCompiled
    _updateFromServerFilt: Dict = clientGridUpdateFromServerFilt
    _logger: logging.Logger = logger
