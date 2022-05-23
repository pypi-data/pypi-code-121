import logging
from typing import Dict

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.tuples.ItemKeyIndexUpdateDateTuple import (
    ItemKeyIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientItemKeyIndexWatchUpdateFromDeviceFilt = {
    "key": "clientItemKeyIndexWatchUpdateFromDevice"
}
clientItemKeyIndexWatchUpdateFromDeviceFilt.update(graphDbFilt)


# ModelSet HANDLER
class ItemKeyIndexCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = ItemKeyIndexUpdateDateTuple
    _updateFromServerFilt: Dict = clientItemKeyIndexWatchUpdateFromDeviceFilt
    _logger: logging.Logger = logger
