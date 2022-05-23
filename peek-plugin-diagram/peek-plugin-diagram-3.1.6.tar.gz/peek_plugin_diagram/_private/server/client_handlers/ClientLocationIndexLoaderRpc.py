import logging
from typing import Optional

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_core_search._private.storage.EncodedSearchObjectChunk import (
    EncodedSearchObjectChunk,
)
from peek_plugin_base.PeekVortexUtil import peekServerName, peekBackendNames
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.LocationIndex import LocationIndexCompiled
from peek_plugin_diagram._private.storage.ModelSet import ModelSet
from sqlalchemy import select
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class ClientLocationIndexLoaderRpc(ACIChunkLoadRpcABC):
    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadLocationIndexes.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=60,
        additionalFilt=diagramFilt,
        deferToThread=True,
    )
    def loadLocationIndexes(self, offset: int, count: int) -> Optional[bytes]:
        """Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        chunkTable = LocationIndexCompiled.__table__
        msTable = ModelSet.__table__

        sql = (
            select(
                [
                    chunkTable.c.indexBucket,
                    chunkTable.c.blobData,
                    chunkTable.c.lastUpdate,
                    msTable.c.key,
                ]
            )
            .select_from(chunkTable.join(msTable))
            .order_by(chunkTable.c.indexBucket)
            .offset(offset)
            .limit(count)
        )

        return self.ckiInitialLoadChunksPayloadBlocking(
            offset, count, LocationIndexCompiled, sql
        )
