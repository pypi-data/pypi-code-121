from typing import Optional

from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_core_search._private.PluginNames import searchTuplePrefix


@addTupleType
class KeywordAutoCompleteTupleAction(TupleActionABC):
    """Keyword Auto Complete Tuple

    This tuple represents the details of a search result.
    """

    __tupleType__ = searchTuplePrefix + "KeywordAutoCompleteTupleAction"

    #:  The property key to restrict to
    objectTypeId: Optional[int] = TupleField()

    #:  The property key to restrict to
    propertyName: Optional[str] = TupleField()

    #:  The search string to search for
    searchString: str = TupleField()
