import logging

from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler

from peek_core_user._private.PluginNames import userPluginFilt
from peek_core_user._private.storage.LdapSetting import LdapSetting

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.LdapSetting"}
filtKey.update(userPluginFilt)


# This is the CRUD hander
class __CrudHandler(OrmCrudHandler):
    pass


# This method creates an instance of the handler class.
def makeLdapSettingeHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, LdapSetting, filtKey, retreiveAll=True)

    return handler
