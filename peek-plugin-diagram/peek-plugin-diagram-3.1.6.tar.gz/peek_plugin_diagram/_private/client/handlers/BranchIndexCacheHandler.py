import logging
from typing import Dict

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.tuples.branch.BranchIndexUpdateDateTuple import (
    BranchIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientBranchIndexWatchUpdateFromDeviceFilt = {
    "key": "clientBranchIndexWatchUpdateFromDevice"
}
clientBranchIndexWatchUpdateFromDeviceFilt.update(diagramFilt)


# ModelSet HANDLER
class BranchIndexCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = BranchIndexUpdateDateTuple
    _updateFromServerFilt: Dict = clientBranchIndexWatchUpdateFromDeviceFilt
    _logger: logging.Logger = logger
