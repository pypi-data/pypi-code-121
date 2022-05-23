from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_abstract_chunked_data_loader.private.server.admin_backend.AppSettingHandler import (
    makeAppSetttingsHandler,
)
from peek_abstract_chunked_data_loader.private.server.admin_backend.CustomAttrTableHandler import (
    makeCustomAttrTableHandler,
)
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_abstract_chunked_data_loader.private.server.admin_backend.CustomHeaderTableHandler import (
    makeCustomHeaderTableHandler,
)
from .SettingPropertyHandler import makeSettingPropertyHandler


def makeAdminBackendHandlers(
    dbSessionCreator: DbSessionCreator, observable: TupleDataObservableHandler
):
    yield makeAppSetttingsHandler(dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)

    yield makeCustomAttrTableHandler(observable, dbSessionCreator)
    yield makeCustomHeaderTableHandler(observable, dbSessionCreator)
