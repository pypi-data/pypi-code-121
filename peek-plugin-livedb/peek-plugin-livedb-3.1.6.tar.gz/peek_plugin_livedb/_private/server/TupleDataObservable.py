from peek_plugin_livedb._private.tuples.AdminStatusTuple import AdminStatusTuple
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_livedb._private.PluginNames import livedbFilt
from peek_plugin_livedb._private.PluginNames import livedbObservableName
from peek_plugin_livedb._private.server.controller.AdminStatusController import (
    AdminStatusController,
)
from peek_plugin_livedb._private.server.tuple_providers.AdminStatusTupleProvider import (
    AdminStatusTupleProvider,
)


def makeTupleDataObservableHandler(
    ormSessionCreator, adminStatusController: AdminStatusController
):
    """ " Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param adminStatusController:
    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=livedbObservableName, additionalFilt=livedbFilt
    )

    # # Register TupleProviders here
    tupleObservable.addTupleProvider(
        AdminStatusTuple.tupleName(), AdminStatusTupleProvider(adminStatusController)
    )
    return tupleObservable
