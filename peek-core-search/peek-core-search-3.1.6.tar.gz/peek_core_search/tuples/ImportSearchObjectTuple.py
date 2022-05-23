from typing import List, Dict

from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search.tuples.ImportSearchObjectRouteTuple import (
    ImportSearchObjectRouteTuple,
)
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class ImportSearchObjectTuple(Tuple):
    """Import Search Object

    This tuple is used by other plugins to load objects into the search index.

    """

    __tupleType__ = searchTuplePrefix + "ImportSearchObjectTuple"

    #:  The unique key for this object
    # This key will be indexed as a full keyword, do not include the key in the keywords
    key: str = TupleField()

    #:  The type of this object
    objectType: str = TupleField()

    #:  Full Keywords
    # The keywords to index that allows the user to search by partial keywords
    # The key of the property will match of create a new "SearchProperty"
    fullKeywords: Dict[str, str] = TupleField({})

    #:  Partial Keywords
    # The keywords to index that allows the user to search by partial keywords
    # The key of the property will match of create a new "SearchProperty"
    partialKeywords: Dict[str, str] = TupleField({})

    #:  The color
    routes: List[ImportSearchObjectRouteTuple] = TupleField([])
