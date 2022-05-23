from peek_plugin_eventdb._private.server.tuple_selector_mappers.NewEventTSUpdateMapper import (
    NewEventTSUpdateMapper,
)
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_eventdb._private.PluginNames import eventdbFilt
from peek_plugin_eventdb._private.PluginNames import eventdbObservableName
from peek_plugin_eventdb._private.server.controller.AdminStatusController import (
    AdminStatusController,
)
from peek_plugin_eventdb._private.server.tuple_providers.AdminStatusTupleProvider import (
    AdminStatusTupleProvider,
)
from peek_plugin_eventdb._private.server.tuple_providers.EventDBEventTupleProvider import (
    EventDBEventTupleProvider,
)
from peek_plugin_eventdb._private.server.tuple_providers.EventDBModelSetTableTupleProvider import (
    EventDBModelSetTableTupleProvider,
)
from peek_plugin_eventdb._private.server.tuple_providers.EventDBPropertyTupleProvider import (
    EventDBPropertyTupleProvider,
)
from peek_plugin_eventdb._private.storage.EventDBModelSetTable import (
    EventDBModelSetTable,
)
from peek_plugin_eventdb._private.tuples.AdminStatusTuple import AdminStatusTuple
from peek_plugin_eventdb.tuples.EventDBEventTuple import EventDBEventTuple
from peek_plugin_eventdb.tuples.EventDBPropertyTuple import EventDBPropertyTuple


def makeTupleDataObservableHandler(
    ormSessionCreator: DbSessionCreator, adminStatusController: AdminStatusController
):
    """ " Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param adminStatusController:
    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=eventdbObservableName, additionalFilt=eventdbFilt
    )

    # Add the tuple selector update mappers
    tupleObservable.addTupleSelectorUpdateMapper(NewEventTSUpdateMapper())

    # Admin Tuple Observers
    tupleObservable.addTupleProvider(
        AdminStatusTuple.tupleName(), AdminStatusTupleProvider(adminStatusController)
    )

    tupleObservable.addTupleProvider(
        EventDBModelSetTable.tupleName(),
        EventDBModelSetTableTupleProvider(ormSessionCreator),
    )

    # UI Tuple Observers
    tupleObservable.addTupleProvider(
        EventDBEventTuple.tupleName(), EventDBEventTupleProvider(ormSessionCreator)
    )

    tupleObservable.addTupleProvider(
        EventDBPropertyTuple.tupleName(),
        EventDBPropertyTupleProvider(ormSessionCreator),
    )
    return tupleObservable
