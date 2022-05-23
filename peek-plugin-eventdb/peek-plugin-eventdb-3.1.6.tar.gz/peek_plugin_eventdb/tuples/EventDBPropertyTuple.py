from typing import Optional, List

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from peek_plugin_eventdb.tuples.EventDBPropertyValueTuple import (
    EventDBPropertyValueTuple,
)


@addTupleType
class EventDBPropertyTuple(Tuple):
    """Event DB Property Tuple

    This tuple stores the name of a property in the alarm / event that the user
    can filter on.

    // modelSetKey: The model that this property applies to.
    modelSetKey: string;

    // key: The unique id of this property within this model set, it must match
    //         the value of a key in the EventDBEventTuple.value json object.
    key: string;

    // name: The name to display to the user in a UI.
    name: string;

    // order: The order of this field
    order: number;

    // comment: The tooltip to display to the user in a UI.
    comment: string | null;

    // useForFilter: Can the user type free text in this field ?
    useForFilter: boolean | null;

    // useForDisplay: Can the user choose to see this
    useForDisplay: boolean | null;

    // useForPopup: Should this ID be used for popping up the DocDB
    useForPopup: boolean | null;

    // FOR DISPLAY
    // displayByDefaultOnSummaryView: Is this field visible by default when showing a
    //      summary alarm / event list.
    displayByDefaultOnSummaryView: boolean | null;

    // FOR DISPLAY
    // displayByDefaultOnDetailView: Is this field visible by default when showing a
    //      details/full alarm / event list.
    displayByDefaultOnDetailView: boolean | null;

    // FOR FILTER
    // showFilterAs: How should the filter be displayed to the user.
    showFilterAs: number | null;

    // FOR FILTER and FOR DISPLAY
    values: EventDBPropertyValueTuple[] | null;

    """

    __tupleType__ = eventdbTuplePrefix + "EventDBPropertyTuple"

    SHOW_FILTER_AS_FREE_TEXT = 1
    SHOW_FILTER_SELECT_MANY = 2
    SHOW_FILTER_SELECT_ONE = 3

    modelSetKey: str = TupleField()
    key: str = TupleField()
    name: str = TupleField()
    order: int = TupleField()
    comment: Optional[str] = TupleField()

    useForFilter: Optional[bool] = TupleField()
    useForDisplay: Optional[bool] = TupleField()
    useForPopup: Optional[bool] = TupleField()

    displayByDefaultOnSummaryView: Optional[bool] = TupleField()
    displayByDefaultOnDetailView: Optional[bool] = TupleField()

    showFilterAs: Optional[int] = TupleField()

    values: Optional[List[EventDBPropertyValueTuple]] = TupleField()
