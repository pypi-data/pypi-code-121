#!/usr/bin/env python
""" 
 *  Copyright Synerty Pty Ltd 2020
 *
 *  This sw_upload is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this sw_upload are reserved by
 *  Synerty Pty Ltd
 *
"""
import logging
import os

from pytmpdir.Directory import DirSettings
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

from peek_platform.util.LogUtil import setupPeekLogger
from peek_plugin_base.PeekVortexUtil import peekStorageName
from peek_storage_service import importPackages
from peek_storage_service._private.storage import setupDbConn
from peek_storage_service._private.storage.DeclarativeBase import metadata

setupPeekLogger(peekStorageName)

from twisted.internet import reactor, defer

from txhttputil.site.SiteUtil import setupSite

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor


def setupPlatform():
    from peek_platform import PeekPlatformConfig

    PeekPlatformConfig.componentName = peekStorageName

    # Tell the platform classes about our instance of the pluginSwInstallManager
    from peek_storage_service._private.service.sw_install.PluginSwInstallManager import (
        PluginSwInstallManager,
    )

    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_storage_service._private.service.sw_install.PeekSwInstallManager import (
        PeekSwInstallManager,
    )

    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_storage_service._private.plugin.StoragePluginLoader import (
        StoragePluginLoader,
    )

    PeekPlatformConfig.pluginLoader = StoragePluginLoader()

    # The config depends on the componentName, order is important
    from peek_storage_service._private.service.PeekStorageConfig import (
        PeekStorageConfig,
    )

    PeekPlatformConfig.config = PeekStorageConfig()

    # Update the version in the config file
    from peek_storage_service import __version__

    PeekPlatformConfig.config.platformVersion = __version__

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)

    # Enable deferred debugging if DEBUG is on.
    if logging.root.level == logging.DEBUG:
        defer.setDebugging(True)

    # If we need to enable memory debugging, turn that on.
    if PeekPlatformConfig.config.loggingDebugMemoryMask:
        from peek_platform.util.MemUtil import setupMemoryDebugging

        setupMemoryDebugging(
            PeekPlatformConfig.componentName,
            PeekPlatformConfig.config.loggingDebugMemoryMask,
        )

    # Set the reactor thread count
    reactor.suggestThreadPoolSize(PeekPlatformConfig.config.twistedThreadPoolSize)

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = PeekPlatformConfig.config.tmpPath


def startListening():
    from peek_platform import PeekPlatformConfig

    from peek_storage_service._private.service.StorageSiteResource import (
        setupPlatformSite,
    )
    from peek_storage_service._private.service.StorageSiteResource import (
        platformSiteRoot,
    )

    setupPlatformSite()

    platformCfg = PeekPlatformConfig.config.platformHttpServer
    setupSite(
        "Peek Platform Data Exchange",
        platformSiteRoot,
        portNum=platformCfg.sitePort,
        enableLogin=False,
        redirectFromHttpPort=platformCfg.redirectFromHttpPort,
        sslBundleFilePath=platformCfg.sslBundleFilePath,
    )

    VortexFactory.createTcpServer(
        name=PeekPlatformConfig.componentName,
        port=PeekPlatformConfig.config.peekStorageVortexTcpPort,
    )


def main():
    setupPlatform()
    from peek_platform import PeekPlatformConfig
    import peek_storage_service

    # Configure sqlalchemy
    setupDbConn(
        metadata=metadata,
        dbEngineArgs=PeekPlatformConfig.config.dbEngineArgs,
        dbConnectString=PeekPlatformConfig.config.dbConnectString,
        alembicDir=os.path.join(
            os.path.dirname(peek_storage_service._private.__file__), "alembic"
        ),
    )

    # Force model migration
    from peek_storage_service._private.storage import dbConn

    dbConn.migrate()

    # Import remaining components
    importPackages()

    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.stopOptionalPlugins
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.stopCorePlugins
    )

    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.unloadOptionalPlugins
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.unloadCorePlugins
    )

    # Load all plugins
    d = PeekPlatformConfig.pluginLoader.loadCorePlugins()
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins())
    d.addCallback(lambda _: startListening())
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins())
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins())

    def startedSuccessfully(_):
        logger.info(
            "Peek Server is running, version=%s",
            PeekPlatformConfig.config.platformVersion,
        )
        return _

    d.addErrback(vortexLogFailure, logger, consumeError=True)
    d.addCallback(startedSuccessfully)

    reactor.run()


if __name__ == "__main__":
    main()
