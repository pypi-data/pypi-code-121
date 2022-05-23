from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_docdb_generic_menu._private.PluginNames import docDbGenericMenuFilt
from peek_plugin_docdb_generic_menu._private.PluginNames import (
    docDbGenericMenuObservableName,
)

from .tuple_providers.DocDbGenericMenuTupleProvider import DocDbGenericMenuTupleProvider
from peek_plugin_docdb_generic_menu._private.storage.DocDbGenericMenuTuple import (
    DocDbGenericMenuTuple,
)


def makeTupleDataObservableHandler(ormSessionCreator):
    """ " Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=docDbGenericMenuObservableName,
        additionalFilt=docDbGenericMenuFilt,
    )

    # Register TupleProviders here
    tupleObservable.addTupleProvider(
        DocDbGenericMenuTuple.tupleName(),
        DocDbGenericMenuTupleProvider(ormSessionCreator),
    )
    return tupleObservable
