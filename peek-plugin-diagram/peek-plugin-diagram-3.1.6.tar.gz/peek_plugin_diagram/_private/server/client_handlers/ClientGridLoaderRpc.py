import logging
from typing import List, Optional

from vortex.DeferUtil import vortexLogFailure
from vortex.rpc.RPC import vortexRPC

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_plugin_base.PeekVortexUtil import peekServerName, peekBackendNames
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndexCompiled

logger = logging.getLogger(__name__)


class ClientGridLoaderRpc(ACIChunkLoadRpcABC):
    def __init__(self, liveDbWatchController, dbSessionCreator):
        ACIChunkLoadRpcABC.__init__(self, dbSessionCreator)
        self._liveDbWatchController = liveDbWatchController

    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadGrids.start(funcSelf=self)
        yield self.updateClientWatchedGrids.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=diagramFilt,
        deferToThread=True,
    )
    def loadGrids(self, offset: int, count: int) -> Optional[bytes]:
        return self.ckiInitialLoadChunksPayloadBlocking(
            offset, count, GridKeyIndexCompiled
        )

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        additionalFilt=diagramFilt,
    )
    def updateClientWatchedGrids(self, clientId: str, gridKeys: List[str]) -> None:
        """Update Client Watched Grids

        Tell the server that these grids are currently being watched by users.

        :param clientId: A unique identifier of the client (Maybe it's vortex uuid)
        :param gridKeys: A list of grid keys that this client is observing.
        :returns: Nothing
        """

        d = self._liveDbWatchController.updateClientWatchedGrids(clientId, gridKeys)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
