from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbDoesKeyExistTuple(Tuple):
    """Does Key Exist Tuple"""

    __tupleType__ = graphDbTuplePrefix + "GraphDbDoesKeyExistTuple"

    #:  Does the key exist in the model
    exists: bool = TupleField()
