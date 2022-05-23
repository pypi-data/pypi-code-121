import logging
from typing import Dict

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples import ACIUpdateDateTupleABC
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.tuples.SegmentIndexUpdateDateTuple import (
    SegmentIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientSegmentWatchUpdateFromDeviceFilt = {"key": "clientSegmentWatchUpdateFromDevice"}
clientSegmentWatchUpdateFromDeviceFilt.update(graphDbFilt)


# ModelSet HANDLER
class SegmentCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = SegmentIndexUpdateDateTuple
    _updateFromServerFilt: Dict = clientSegmentWatchUpdateFromDeviceFilt
    _logger: logging.Logger = logger
