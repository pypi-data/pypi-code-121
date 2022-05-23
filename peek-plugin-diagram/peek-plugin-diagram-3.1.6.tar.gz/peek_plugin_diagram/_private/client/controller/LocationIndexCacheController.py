import logging

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.server.client_handlers.ClientLocationIndexLoaderRpc import (
    ClientLocationIndexLoaderRpc,
)
from peek_plugin_diagram._private.tuples.location_index.EncodedLocationIndexTuple import (
    EncodedLocationIndexTuple,
)

logger = logging.getLogger(__name__)

clientLocationIndexUpdateFromServerFilt = dict(
    key="clientLocationIndexUpdateFromServer"
)
clientLocationIndexUpdateFromServerFilt.update(diagramFilt)


class LocationIndexCacheController(ACICacheControllerABC):
    """Disp Key Cache Controller

    The encodedChunk cache controller stores all the locationIndexs in memory, allowing fast access from
    the mobile and desktop devices.

    """

    _ChunkedTuple = EncodedLocationIndexTuple
    _chunkLoadRpcMethod = ClientLocationIndexLoaderRpc.loadLocationIndexes
    _updateFromServerFilt = clientLocationIndexUpdateFromServerFilt
    _logger = logger
