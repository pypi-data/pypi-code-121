import logging
from collections import defaultdict
from typing import List, Optional

from peek_plugin_base.storage.LoadPayloadPgUtil import (
    getTuplesPayloadBlocking,
    LoadPayloadTupleResult,
)
from peek_plugin_eventdb._private.server.controller.EventDBController import (
    EventDBController,
)
from peek_plugin_eventdb._private.storage.EventDBModelSetTable import (
    getOrCreateEventDBModelSet,
)
from peek_plugin_eventdb.server.EventDBReadApiABC import EventDBReadApiABC
from peek_plugin_eventdb.tuples.EventDBEventTuple import EventDBEventTuple
from rx.subjects import Subject
from sqlalchemy import select
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class EventDBReadApi(EventDBReadApiABC):
    def __init__(self):
        self._eventdbController = None
        self._dbSessionCreator = None
        self._dbEngine = None

        self._newEventsSubject = defaultdict(Subject)

    def setup(self, eventdbController: EventDBController, dbSessionCreator, dbEngine):
        self._eventdbController = eventdbController
        self._dbSessionCreator = dbSessionCreator
        self._dbEngine = dbEngine

    def shutdown(self):
        pass

    def newEventsObservable(self, modelSetKey: str) -> Subject:
        return self._newEventsSubject[modelSetKey]
