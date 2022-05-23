import logging

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)

peekClientObservableName = "peek_field_service"

observable = TupleDataObservableHandler(
    observableName=peekClientObservableName,
    additionalFilt={"plugin": "peek_field_service"},
    subscriptionsEnabled=True,
)

# observable.addTupleProvider(PluginAppTileTuple.tupleName(), HomeAppTileTupleProvider())
