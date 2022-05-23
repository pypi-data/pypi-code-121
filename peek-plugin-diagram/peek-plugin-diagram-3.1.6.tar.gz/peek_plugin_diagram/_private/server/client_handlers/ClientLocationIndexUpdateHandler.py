import logging
from typing import List, Dict

from sqlalchemy import select

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkUpdateHandlerABC import (
    ACIChunkUpdateHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_plugin_diagram._private.client.controller.LocationIndexCacheController import (
    clientLocationIndexUpdateFromServerFilt,
)
from peek_plugin_diagram._private.storage.LocationIndex import LocationIndexCompiled
from peek_plugin_diagram._private.storage.ModelSet import ModelSet

logger = logging.getLogger(__name__)


class ClientLocationIndexUpdateHandler(ACIChunkUpdateHandlerABC):
    _ChunkedTuple: ACIEncodedChunkTupleABC = LocationIndexCompiled
    _updateFromServerFilt: Dict = clientLocationIndexUpdateFromServerFilt
    _logger: logging.Logger = logger

    @classmethod
    def _makeLoadSql(cls, chunkKeys: List[str]):
        chunkTable = LocationIndexCompiled.__table__
        msTable = ModelSet.__table__

        return (
            select(
                [
                    chunkTable.c.indexBucket,
                    chunkTable.c.blobData,
                    chunkTable.c.lastUpdate,
                    msTable.c.key,
                ]
            )
            .select_from(chunkTable.join(msTable))
            .where(chunkTable.c.indexBucket.in_(chunkKeys))
        )
