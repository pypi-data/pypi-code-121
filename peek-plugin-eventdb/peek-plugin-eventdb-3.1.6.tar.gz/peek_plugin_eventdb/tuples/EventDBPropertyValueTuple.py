from typing import Optional

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix


@addTupleType
class EventDBPropertyValueTuple(Tuple):
    """Event DB Property Value Tuple

    This tuple is an option that the user can select for each property.

    For example:

    Property = Alarm Class
    Property Value = Class 1
    Property Value = Class 2

    name: The name of this property value that is displayed to the user.

    value: The value that matches
       EvenDBEventTuple.value[property.key] == propertyValue.value

    color: If this property has a color then define it here.
           the first property value with a color will be applied
           ordered by property.order

    comment: The tooltip to display to the user in a UI.

    """

    __tupleType__ = eventdbTuplePrefix + "EventDBPropertyValueTuple"

    name: str = TupleField()
    value: str = TupleField()
    color: str = TupleField()
    comment: Optional[str] = TupleField()
