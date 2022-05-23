from typing import Dict

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_core_search._private.PluginNames import searchTuplePrefix


@addTupleType
class SearchIndexUpdateDateTuple(Tuple, ACIUpdateDateTupleABC):
    """Search Index Update Date Tuple

    This tuple represents the state of the chunks in the cache.
    Each chunkKey has a lastUpdateDate as a string, this is used for offline caching
    all the chunks.
    """

    __tupleType__ = searchTuplePrefix + "SearchIndexUpdateDateTuple"

    # Improve performance of the JSON serialisation
    __rawJonableFields__ = ("initialLoadComplete", "updateDateByChunkKey")

    initialLoadComplete: bool = TupleField()
    updateDateByChunkKey: Dict[str, str] = TupleField({})

    @property
    def ckiUpdateDateByChunkKey(self):
        return self.updateDateByChunkKey
