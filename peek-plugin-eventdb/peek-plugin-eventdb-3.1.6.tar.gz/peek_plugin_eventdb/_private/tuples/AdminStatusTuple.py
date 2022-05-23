from datetime import datetime

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix


@addTupleType
class AdminStatusTuple(Tuple):
    __tupleType__ = eventdbTuplePrefix + "AdminStatusTuple"

    addedEvents: int = TupleField(0)
    removedEvents: int = TupleField(0)
    updatedAlarmFlags: int = TupleField(0)
    lastActivity: datetime = TupleField()
