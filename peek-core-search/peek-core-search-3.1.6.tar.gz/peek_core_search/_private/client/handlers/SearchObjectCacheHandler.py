import logging
from typing import Dict

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.tuples.search_object.SearchObjectUpdateDateTuple import (
    SearchObjectUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientSearchObjectWatchUpdateFromDeviceFilt = {
    "key": "clientSearchObjectWatchUpdateFromDevice"
}
clientSearchObjectWatchUpdateFromDeviceFilt.update(searchFilt)


# ModelSet HANDLER
class SearchObjectCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = SearchObjectUpdateDateTuple
    _updateFromServerFilt: Dict = clientSearchObjectWatchUpdateFromDeviceFilt
    _logger: logging.Logger = logger
