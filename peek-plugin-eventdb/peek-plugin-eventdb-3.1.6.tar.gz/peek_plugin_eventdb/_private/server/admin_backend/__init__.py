from .EventDBPropertyTableHandler import makeEventDBPropertyTupleHandler
from .SettingPropertyHandler import makeSettingPropertyHandler
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeAdminBackendHandlers(
    tupleObservable: TupleDataObservableHandler, dbSessionCreator
):
    yield makeEventDBPropertyTupleHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)
