import logging
from typing import Optional

from vortex.rpc.RPC import vortexRPC

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.storage.EncodedSearchIndexChunk import (
    EncodedSearchIndexChunk,
)
from peek_core_search._private.storage.EncodedSearchObjectChunk import (
    EncodedSearchObjectChunk,
)
from peek_plugin_base.PeekVortexUtil import peekServerName, peekBackendNames

logger = logging.getLogger(__name__)


class ClientChunkLoadRpc(ACIChunkLoadRpcABC):
    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadSearchIndexChunks.start(funcSelf=self)
        yield self.loadSearchObjectChunks.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=60,
        additionalFilt=searchFilt,
        deferToThread=True,
    )
    def loadSearchIndexChunks(self, offset: int, count: int) -> Optional[bytes]:
        """Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        return self.ckiInitialLoadChunksPayloadBlocking(
            offset, count, EncodedSearchIndexChunk
        )

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=60,
        additionalFilt=searchFilt,
        deferToThread=True,
    )
    def loadSearchObjectChunks(self, offset: int, count: int) -> Optional[bytes]:
        """Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        return self.ckiInitialLoadChunksPayloadBlocking(
            offset, count, EncodedSearchObjectChunk
        )
