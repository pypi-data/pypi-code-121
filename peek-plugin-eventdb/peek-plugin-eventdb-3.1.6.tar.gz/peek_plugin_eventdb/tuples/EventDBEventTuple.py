from vortex.Tuple import Tuple, addTupleType

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix


@addTupleType
class EventDBEventTuple(Tuple):
    """Event DB Event Tuple

    This tuple stores a value of a key in the Event DB database.

    datetime: is a timezone aware datetime
    key: is the key of this alarm or event (Optional)
    value: is the value of this event.

    """

    __tupleType__ = eventdbTuplePrefix + "EventDBEventTuple"
    __slots__ = ("dateTime", "key", "isAlarm", "value")

    @classmethod
    def sqlCoreLoad(cls, row):
        return EventDBEventTuple(
            datetime=row.datetime, key=row.key, isAlarm=row.isAlarm, value=row.value
        )
