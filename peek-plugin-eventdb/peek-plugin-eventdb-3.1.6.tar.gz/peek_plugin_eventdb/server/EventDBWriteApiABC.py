from abc import ABCMeta, abstractmethod
from typing import List

from twisted.internet.defer import Deferred


class EventDBWriteApiABC(metaclass=ABCMeta):
    @abstractmethod
    def addEvents(self, modelSetKey: str, eventsEncodedPayload: str) -> Deferred:
        """Add Events

        Add events to the EventDB

        :param modelSetKey:  The name of the model set for the EventDB
        :param eventsEncodedPayload: An encoded Payload containing a
         list of events to insert.

        :return: A deferred that fires when the insert is complete.
        :rtype: None

        """

    @abstractmethod
    def removeEvents(self, modelSetKey: str, eventKeys: List[str]) -> Deferred:
        """Remove Events

        Remove events from the EventDB

        :param modelSetKey:  The name of the model set for the EventDB
        :param eventKeys: An list of event keys to remove.

        :return: A deferred that fires when the removal is complete.
        :rtype: None

        """

    @abstractmethod
    def updateAlarmFlags(
        self, modelSetKey: str, eventKeys: List[str], alarmFlag: bool
    ) -> Deferred:
        """Update Alarm Flag

        Change the value of the alarm flag for alarms.

        :param modelSetKey:  The name of the model set for the EventDB
        :param eventKeys: An list of event keys to update the alarm flag.
        :param alarmFlag: The value to set the alarm flag to.

        :return: A deferred that fires when the update is complete.
        :rtype: None

        """

    @abstractmethod
    def replaceProperties(
        self, modelSetKey: str, propertiesEncodedPayload: str
    ) -> Deferred:
        """Replace Properties

        Create or Replace the properties for a model set of events.

        :param modelSetKey:  The name of the model set for the EventDB
        :param propertiesEncodedPayload: An encoded Payload containing a
                payload.tuples=List[EventDBPropertyTuple]
         list of events to insert.

        :return: A deferred that fires when the create / update is complete.
        :rtype: None

        """
