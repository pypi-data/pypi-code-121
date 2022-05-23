from typing import Union, List

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from peek_plugin_eventdb.tuples.EventDBPropertyTuple import EventDBPropertyTuple
from peek_plugin_eventdb.tuples.EventDBPropertyValueTuple import (
    EventDBPropertyValueTuple,
)


@addTupleType
class EventDBPropertyCriteriaTuple(Tuple):
    """Event DB Property Criteria Tuple

    This tuple stores the criteria of alarms and events to retrieve.

    """

    __tupleType__ = eventdbTuplePrefix + "EventDBPropertyCriteriaTuple"

    property: EventDBPropertyTuple = TupleField()
    value: Union[List[str], str] = TupleField()
