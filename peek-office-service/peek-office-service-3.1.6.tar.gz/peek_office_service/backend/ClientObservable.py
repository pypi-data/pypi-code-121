import logging

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)

peekClientObservableName = "peek_office_service"

observable = TupleDataObservableHandler(
    observableName=peekClientObservableName,
    additionalFilt={"plugin": "peek_office_service"},
    subscriptionsEnabled=True,
)

# observable.addTupleProvider(PluginAppTileTuple.tupleName(), HomeAppTileTupleProvider())
