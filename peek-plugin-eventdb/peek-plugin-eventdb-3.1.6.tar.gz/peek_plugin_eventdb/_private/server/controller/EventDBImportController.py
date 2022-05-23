import logging
from datetime import datetime
from typing import List

import pytz
from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.RunPyInPg import runPyInPg
from peek_plugin_eventdb._private.server.EventDBReadApi import EventDBReadApi
from peek_plugin_eventdb._private.server.controller.AdminStatusController import (
    AdminStatusController,
)
from peek_plugin_eventdb._private.server.controller.EventDBImportEventsInPgTask import (
    EventDBImportEventsInPgTask,
)
from peek_plugin_eventdb._private.server.controller.EventDBImportPropertiesInPgTask import (
    EventDBImportPropertiesInPgTask,
)
from peek_plugin_eventdb._private.server.tuple_selector_mappers.NewEventTSUpdateMapper import (
    NewEventsTupleSelector,
)
from peek_plugin_eventdb._private.storage.EventDBPropertyTable import (
    EventDBPropertyTable,
)
from peek_plugin_eventdb.tuples.EventDBPropertyTuple import EventDBPropertyTuple

logger = logging.getLogger(__name__)


class EventDBImportController:
    """EventDB Import Controller"""

    def __init__(
        self,
        dbSessionCreator: DbSessionCreator,
        statusController: AdminStatusController,
        tupleObservable: TupleDataObservableHandler,
    ):
        self._dbSessionCreator = dbSessionCreator
        self._statusController = statusController
        self._tupleObservable = tupleObservable

    def setReadApi(self, readApi: EventDBReadApi):
        self._readApi = readApi

    def shutdown(self):
        self._readApi = None
        self._tupleObservable = None

    @inlineCallbacks
    def importEvents(self, modelSetKey: str, eventsEncodedPayload: str) -> Deferred:
        count, maxDate, minDate = yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportEventsInPgTask.importEvents,
            None,
            modelSetKey,
            eventsEncodedPayload,
        )

        # Notify anyone watching the events that new ones have arrived.
        if count:
            self._tupleObservable.notifyOfTupleUpdate(
                NewEventsTupleSelector(minDate, maxDate)
            )

        self._statusController.status.addedEvents += count
        self._statusController.status.lastActivity = datetime.now(pytz.utc)
        self._statusController.notify()

    @inlineCallbacks
    def deleteEvents(self, modelSetKey: str, eventKeys: List[str]) -> Deferred:
        count = yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportEventsInPgTask.deleteEvents,
            None,
            modelSetKey,
            eventKeys,
        )

        self._statusController.status.removedEvents += count
        self._statusController.status.lastActivity = datetime.now(pytz.utc)
        self._statusController.notify()

    @inlineCallbacks
    def updateAlarmFlags(
        self, modelSetKey: str, eventKeys: List[str], alarmFlag: bool
    ) -> Deferred:
        count = yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportEventsInPgTask.updateAlarmFlags,
            None,
            modelSetKey,
            eventKeys,
            alarmFlag,
        )

        self._statusController.status.updatedAlarmFlags += count
        self._statusController.status.lastActivity = datetime.now(pytz.utc)
        self._statusController.notify()

    @inlineCallbacks
    def replaceProperties(
        self, modelSetKey: str, propertiesEncodedPayload: str
    ) -> Deferred:
        yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportPropertiesInPgTask.replaceProperties,
            None,
            modelSetKey,
            propertiesEncodedPayload,
        )

        tupleSelector = TupleSelector(EventDBPropertyTable.tupleName(), {})
        self._tupleObservable.notifyOfTupleUpdate(tupleSelector)

        tupleSelector = TupleSelector(EventDBPropertyTuple.tupleName(), {})
        self._tupleObservable.notifyOfTupleUpdate(tupleSelector)
