from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_livedb._private.PluginNames import livedbTuplePrefix


@addTupleType
class AdminStatusTuple(Tuple):
    __tupleType__ = livedbTuplePrefix + "AdminStatusTuple"

    rawValueQueueStatus: bool = TupleField(False)
    rawValueQueueSize: int = TupleField(0)
    rawValueProcessedTotal: int = TupleField(0)
    rawValueLastError: str = TupleField()
