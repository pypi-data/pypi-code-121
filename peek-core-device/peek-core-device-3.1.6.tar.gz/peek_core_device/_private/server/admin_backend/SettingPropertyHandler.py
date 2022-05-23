import logging

from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandlerExtension

from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.storage.Setting import SettingProperty
from peek_core_device._private.storage.Setting import globalSetting
from peek_core_device._private.tuples.ClientSettingsTuple import \
    ClientSettingsTuple

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.SettingProperty"}
filtKey.update(deviceFilt)


# This is the CRUD handler
class __CrudHandler(OrmCrudHandler):
    # The UI only edits the global settings
    # You could get more complicated and have the UI edit different groups of settings.
    def createDeclarative(self, session, payloadFilt):
        return [p for p in globalSetting(session).propertyObjects]


class __ExtUpdateObservable(OrmCrudHandlerExtension):
    """Update Observable ORM Crud Extension

    This extension is called after events that will alter data,
    it then notifies the observer.

    """

    def __init__(self, tupleDataObserver: TupleDataObservableHandler):
        self._tupleDataObserver = tupleDataObserver

    def _tellObserver(self, tuple_, tuples, session, payloadFilt):
        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(SettingProperty.tupleName(), {})
        )

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(ClientSettingsTuple.tupleName(), {})
        )

        return True

    afterUpdateCommit = _tellObserver
    afterDeleteCommit = _tellObserver


# This method creates an instance of the handler class.
def makeSettingPropertyHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(
        dbSessionCreator, SettingProperty, filtKey, retreiveAll=True
    )

    handler.addExtension(SettingProperty,
        __ExtUpdateObservable(tupleObservable))
    logger.debug("Started")
    return handler
