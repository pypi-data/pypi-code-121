import logging
from typing import Dict

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkUpdateHandlerABC import (
    ACIChunkUpdateHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_diagram._private.client.controller.BranchIndexCacheController import (
    clientBranchIndexUpdateFromServerFilt,
)
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import (
    BranchIndexEncodedChunk,
)

logger = logging.getLogger(__name__)


class BranchIndexChunkUpdateHandler(ACIChunkUpdateHandlerABC):
    _ChunkedTuple: ACIEncodedChunkTupleABC = BranchIndexEncodedChunk
    _updateFromServerFilt: Dict = clientBranchIndexUpdateFromServerFilt
    _logger: logging.Logger = logger
