import logging
from typing import Dict

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_core_docdb._private.PluginNames import docDbFilt
from peek_core_docdb._private.tuples.DocumentUpdateDateTuple import (
    DocumentUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientDocumentWatchUpdateFromDeviceFilt = {"key": "clientDocumentWatchUpdateFromDevice"}
clientDocumentWatchUpdateFromDeviceFilt.update(docDbFilt)


# ModelSet HANDLER
class DocumentCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = DocumentUpdateDateTuple
    _updateFromServerFilt: Dict = clientDocumentWatchUpdateFromDeviceFilt
    _logger: logging.Logger = logger
