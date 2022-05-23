import logging

from peek_plugin_eventdb.tuples.EventDBPropertyTuple import EventDBPropertyTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

from peek_plugin_eventdb._private.PluginNames import eventdbFilt
from peek_plugin_eventdb._private.storage.EventDBPropertyTable import (
    EventDBPropertyTable,
)

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.EventDBPropertyTuple"}
filtKey.update(eventdbFilt)


# This is the CRUD hander
class __CrudHandler(OrmCrudHandler):
    pass


class __ExtUpdateObservable(OrmCrudHandlerExtension):
    """Update Observable ORM Crud Extension

    This extension is called after events that will alter data,
    it then notifies the observer.

    """

    def __init__(self, tupleDataObserver: TupleDataObservableHandler):
        self._tupleDataObserver = tupleDataObserver

    def afterCreate(self, tuple_, tuples, session, payloadFilt):
        for tuple_ in tuples:
            tuple_.valuesFromAdminUi = tuple_.values

        return True

    def beforeUpdate(self, tuple_, tuples, session, payloadFilt):
        for tuple_ in tuples:
            tuple_.values = tuple_.valuesFromAdminUi

        return True

    def afterUpdate(self, tuple_, tuples, session, payloadFilt):
        for tuple_ in tuples:
            tuple_.valuesFromAdminUi = tuple_.values

        return True

    def _tellObserver(self, tuple_, tuples, session, payloadFilt):
        tupleSelector = TupleSelector(EventDBPropertyTable.tupleName(), {})
        self._tupleDataObserver.notifyOfTupleUpdate(tupleSelector)

        tupleSelector = TupleSelector(EventDBPropertyTuple.tupleName(), {})
        self._tupleDataObserver.notifyOfTupleUpdate(tupleSelector)

        return True

    afterUpdateCommit = _tellObserver
    afterDeleteCommit = _tellObserver


# This method creates an instance of the handler class.
def makeEventDBPropertyTupleHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(
        dbSessionCreator, EventDBPropertyTable, filtKey, retreiveAll=True
    )

    logger.debug("Started")
    handler.addExtension(EventDBPropertyTable, __ExtUpdateObservable(tupleObservable))
    return handler
