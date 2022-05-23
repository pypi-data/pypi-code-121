import logging
import os

from peek_plugin_base.PeekVortexUtil import peekStorageName

logger = logging.getLogger(__name__)


class StorageTestMixin:
    def __init__(self):
        self._dbConn = None

    def setUp(self) -> None:
        from peek_storage_service._private.storage import setupDbConn
        from peek_storage_service._private.storage.DeclarativeBase import metadata
        import peek_storage_service
        from peek_plugin_base.storage.DbConnection import DbConnection
        from peek_storage_service._private.service.PeekStorageConfig import (
            PeekStorageConfig,
        )

        from peek_platform import PeekPlatformConfig

        PeekPlatformConfig.componentName = peekStorageName

        config = PeekStorageConfig()

        alembicDir = os.path.join(
            os.path.dirname(peek_storage_service._private.__file__), "alembic"
        )
        self._dbConn = DbConnection(
            dbConnectString=config.dbConnectString,
            metadata=metadata,
            alembicDir=alembicDir,
            dbEngineArgs=config.dbEngineArgs,
            enableCreateAll=False,
            enableForeignKeys=False,
        )

        self._dbConn.migrate()

    def tearDown(self) -> None:
        self._dbConn.closeAllSessions()
