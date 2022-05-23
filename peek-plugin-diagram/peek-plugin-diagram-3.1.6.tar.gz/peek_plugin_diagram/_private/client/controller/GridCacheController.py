import logging
from typing import Dict, List

from twisted.internet.defer import Deferred
from vortex.DeferUtil import vortexLogFailure
from vortex.PayloadEndpoint import PayloadEndpoint

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.server.client_handlers.ClientGridLoaderRpc import (
    ClientGridLoaderRpc,
)
from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import EncodedGridTuple
from peek_plugin_diagram._private.tuples.grid.GridTuple import GridTuple

logger = logging.getLogger(__name__)

clientGridUpdateFromServerFilt = dict(key="clientGridUpdateFromServer")
clientGridUpdateFromServerFilt.update(diagramFilt)

clientCoordSetUpdateFromServerFilt = dict(key="clientCoordSetUpdateFromServer")
clientCoordSetUpdateFromServerFilt.update(diagramFilt)


class GridCacheController(ACICacheControllerABC):
    """Grid Cache Controller

    The grid cache controller stores all the grids in memory, allowing fast access from
    the mobile and desktop devices.

    NOTE: The grid set endpoint triggers a reload, this is in the case when grid sets
    are enable or disabled. Perhaps the system should just be restarted instead.

    """

    _ChunkedTuple = EncodedGridTuple
    _chunkLoadRpcMethod = ClientGridLoaderRpc.loadGrids
    _updateFromServerFilt = clientGridUpdateFromServerFilt
    _logger = logger

    #: This stores the cache of grid data for the clients
    _cache: Dict[str, GridTuple] = None

    _LOAD_CHUNK_SIZE = 75
    _LOAD_CHUNK_PARALLELISM = 4

    def __init__(self, clientId: str):
        ACICacheControllerABC.__init__(self, clientId)

        self._coordSetEndpoint = PayloadEndpoint(
            clientCoordSetUpdateFromServerFilt, self._processCoordSetPayload
        )

    def _processCoordSetPayload(self, *args, **kwargs):
        d: Deferred = self.reloadCache()
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    def shutdown(self):
        ACICacheControllerABC.shutdown(self)

        self._coordSetEndpoint.shutdown()
        self._coordSetEndpoint = None
