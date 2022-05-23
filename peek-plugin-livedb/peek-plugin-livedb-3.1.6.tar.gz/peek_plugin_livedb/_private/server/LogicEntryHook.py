import logging

from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import (
    PluginServerStorageEntryHookABC,
)
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import (
    PluginServerWorkerEntryHookABC,
)
from peek_plugin_livedb._private.server.controller.LiveDbController import (
    LiveDbController,
)
from peek_plugin_livedb._private.server.controller.LiveDbImportController import (
    LiveDbImportController,
)
from peek_plugin_livedb._private.storage import DeclarativeBase
from peek_plugin_livedb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_livedb._private.tuples import loadPrivateTuples
from peek_plugin_livedb.tuples import loadPublicTuples
from .LiveDBApi import LiveDBApi
from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
from .controller.AdminStatusController import AdminStatusController
from .controller.LiveDbValueUpdateQueueController import (
    LiveDbValueUpdateQueueController,
)
from .controller.MainController import MainController
from ..storage.Setting import VALUE_UPDATER_ENABLED, globalProperties, globalSetting

logger = logging.getLogger(__name__)


class LogicEntryHook(
    PluginLogicEntryHookABC,
    PluginServerStorageEntryHookABC,
    PluginServerWorkerEntryHookABC,
):
    def __init__(self, *args, **kwargs):
        """" Constructor """
        # Call the base classes constructor
        PluginLogicEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

        self._api = None

    def load(self) -> None:
        """Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        self._api = LiveDBApi()
        self._loadedObjects.append(self._api)

        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()
        logger.debug("Loaded")

    @property
    def dbMetadata(self):
        return DeclarativeBase.metadata

    @inlineCallbacks
    def start(self):
        """Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        # ----------------
        # create the Status Controller
        statusController = AdminStatusController()
        self._loadedObjects.append(statusController)

        # ----------------
        # Create the Tuple Observer
        tupleObservable = makeTupleDataObservableHandler(
            self.dbSessionCreator, statusController
        )
        self._loadedObjects.append(tupleObservable)

        # ----------------
        # Tell the status controller about the Tuple Observable
        statusController.setTupleObservable(tupleObservable)

        # ----------------
        # Initialise the handlers for the admin interface
        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        # ----------------
        # create the Main Controller
        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator, tupleObservable=tupleObservable
        )

        self._loadedObjects.append(mainController)

        # ----------------
        # Create the Action Processor
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # ----------------
        # Create the LiveDB controller
        liveDbController = LiveDbController(self.dbSessionCreator)
        self._loadedObjects.append(liveDbController)

        # ----------------
        # Create the Import Controller
        liveDbImportController = LiveDbImportController(self.dbSessionCreator)
        self._loadedObjects.append(liveDbImportController)

        # ----------------
        # Create the Queue Controller
        queueController = LiveDbValueUpdateQueueController(
            self.dbSessionCreator, statusController
        )
        self._loadedObjects.append(queueController)

        # ----------------
        # Initialise the API object that will be shared with other plugins
        self._api.setup(
            queueController=queueController,
            liveDbController=liveDbController,
            liveDbImportController=liveDbImportController,
            dbSessionCreator=self.dbSessionCreator,
            dbEngine=self.dbEngine,
        )

        # ----------------
        # Start the queue controller

        settings = yield self._loadSettings()

        if settings[VALUE_UPDATER_ENABLED]:
            queueController.start()

        # noinspection PyTypeChecker
        liveDbImportController.setReadApi(self._api.readApi)

        logger.debug("Started")

    def stop(self):
        """Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        self._api = None

        logger.debug("Stopped")

    def unload(self):
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform

        """
        logger.debug("Unloaded")

    @property
    def publishedServerApi(self) -> object:
        """Published Server API

        :return  class that implements the API that can be used by other Plugins on this
        platform service.
        """
        return self._api

    @deferToThreadWrapWithLogger(logger)
    def _loadSettings(self):
        dbSession = self.dbSessionCreator()
        try:
            return {
                globalProperties[p.key]: p.value
                for p in globalSetting(dbSession).propertyObjects
            }

        finally:
            dbSession.close()

    ###### Implement PluginServerWorkerEntryHookABC
