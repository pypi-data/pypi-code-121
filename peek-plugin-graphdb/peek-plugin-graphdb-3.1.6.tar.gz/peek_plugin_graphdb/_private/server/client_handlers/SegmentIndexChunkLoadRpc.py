import logging
from typing import Optional

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_plugin_base.PeekVortexUtil import peekServerName, peekBackendNames
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import GraphDbEncodedChunk
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from sqlalchemy import select
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class SegmentIndexChunkLoadRpc(ACIChunkLoadRpcABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadSegmentChunks.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=60,
        additionalFilt=graphDbFilt,
        deferToThread=True,
    )
    def loadSegmentChunks(self, offset: int, count: int) -> Optional[bytes]:
        """Load Segment Chunks

        Allow the client to incrementally load the chunks.

        """
        chunkTable = GraphDbEncodedChunk.__table__
        msTable = GraphDbModelSet.__table__

        sql = (
            select(
                [
                    msTable.c.key,
                    chunkTable.c.chunkKey,
                    chunkTable.c.encodedData,
                    chunkTable.c.encodedHash,
                    chunkTable.c.lastUpdate,
                ]
            )
            .select_from(chunkTable.join(msTable))
            .order_by(chunkTable.c.chunkKey)
            .offset(offset)
            .limit(count)
        )

        return self.ckiInitialLoadChunksPayloadBlocking(
            offset, count, GraphDbEncodedChunk, sql
        )
