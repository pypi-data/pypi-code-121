import logging

from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler

from peek_core_docdb._private.PluginNames import docDbFilt
from peek_core_docdb._private.storage.DocDbDocument import DocDbDocument

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.DocumentTuple"}
filtKey.update(docDbFilt)


# This is the CRUD hander
class __CrudHandler(OrmCrudHandler):
    def createDeclarative(self, session, payloadFilt):
        return (
            session.query(DocDbDocument)
            .filter(DocDbDocument.key == payloadFilt.get("docKey"))
            .all()
        )


# This method creates an instance of the handler class.
def makeDocumentTableHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, DocDbDocument, filtKey)

    logger.debug("Started")
    return handler
