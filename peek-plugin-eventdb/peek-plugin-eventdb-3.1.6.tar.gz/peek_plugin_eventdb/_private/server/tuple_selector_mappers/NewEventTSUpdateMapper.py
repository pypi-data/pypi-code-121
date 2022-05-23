from datetime import datetime
from typing import List

from peek_plugin_eventdb.tuples.EventDBEventTuple import EventDBEventTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleSelectorUpdateMapperABC


class NewEventsTupleSelector(TupleSelector):
    """New Events Tuple Selector

    This is a tuple selector that is only used to notify our mapper below that new
    events have been imported.

    The mapper then maps to the relevent real tuple selectors
    """

    NAME = "new events imported"

    def __init__(self, minDate: datetime, maxDate: datetime):
        TupleSelector.__init__(self, self.NAME, dict(minDate=minDate, maxDate=maxDate))

    @property
    def minDate(self):
        return self.selector["minDate"]

    @property
    def maxDate(self):
        return self.selector["maxDate"]


class NewEventTSUpdateMapper(TupleSelectorUpdateMapperABC):
    def mapTupleSelector(
        self,
        triggerTupleSelector: TupleSelector,
        allTupleSelectors: List[TupleSelector],
    ) -> List[TupleSelector]:
        if not triggerTupleSelector.name == NewEventsTupleSelector.NAME:
            return []

        eventTss = filter(
            lambda ts: ts.name == EventDBEventTuple.tupleName(), allTupleSelectors
        )

        updateTs: NewEventsTupleSelector = triggerTupleSelector
        minDate = updateTs.minDate
        maxDate = updateTs.maxDate

        results = []
        for tupleSelector in eventTss:
            newestDateTime = tupleSelector.selector.get("newestDateTime")
            oldestDateTime = tupleSelector.selector.get("oldestDateTime")

            isMinInRange = (oldestDateTime is None or oldestDateTime <= minDate) and (
                newestDateTime is None or minDate <= newestDateTime
            )

            isMaxInRange = (oldestDateTime is None or oldestDateTime <= maxDate) and (
                newestDateTime is None or maxDate <= newestDateTime
            )

            if isMinInRange or isMaxInRange:
                results.append(tupleSelector)

        return results
