from abc import ABCMeta, abstractmethod
from typing import List

from rx.subjects import Subject


class EventDBReadApiABC(metaclass=ABCMeta):
    @abstractmethod
    def newEventsObservable(self, modelSetKey: str) -> Subject:
        """Raw Value Update Observable

        Return an observable that fires with lists of C{EventDBEventTuple} tuples
        containing updates to EventDB values.

        :param modelSetKey:  The name of the model set for the EventDB

        :return: An observable that fires when values are updated in the eventdb
        :rtype: Subject[List[EventDBEventTuple]]

        """
