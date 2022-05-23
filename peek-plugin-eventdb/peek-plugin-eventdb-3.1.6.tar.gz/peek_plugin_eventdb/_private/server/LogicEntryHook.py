import logging

from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import (
    PluginServerStorageEntryHookABC,
)
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import (
    PluginServerWorkerEntryHookABC,
)
from peek_plugin_eventdb._private.server.controller.EventDBController import (
    EventDBController,
)
from peek_plugin_eventdb._private.server.controller.EventDBImportController import (
    EventDBImportController,
)
from peek_plugin_eventdb._private.server.download_resources.DownloadEventsResource import (
    DownloadEventsResource,
)
from peek_plugin_eventdb._private.storage import DeclarativeBase
from peek_plugin_eventdb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_eventdb._private.tuples import loadPrivateTuples
from peek_plugin_eventdb.tuples import loadPublicTuples
from txhttputil.site.BasicResource import BasicResource

from .EventDBApi import EventDBApi
from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
from .controller.AdminStatusController import AdminStatusController
from .controller.MainController import MainController

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
        self._api = EventDBApi()
        self._loadedObjects.append(self._api)

        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()
        logger.debug("Loaded")

    @property
    def dbMetadata(self):
        return DeclarativeBase.metadata

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
        # Create the EventDB controller
        eventdbController = EventDBController(self.dbSessionCreator)
        self._loadedObjects.append(eventdbController)

        # ----------------
        # Create the Import Controller
        eventdbImportController = EventDBImportController(
            self.dbSessionCreator, statusController, tupleObservable
        )
        self._loadedObjects.append(eventdbImportController)

        # ----------------
        # Initialise the API object that will be shared with other plugins
        self._api.setup(
            eventdbController=eventdbController,
            eventdbImportController=eventdbImportController,
            dbSessionCreator=self.dbSessionCreator,
            dbEngine=self.dbEngine,
        )

        # ----------------
        # Start the queue controller

        # noinspection PyTypeChecker
        eventdbImportController.setReadApi(self._api.readApi)

        downloadResource = BasicResource()
        eventsResource = DownloadEventsResource(self.dbSessionCreator)
        # noinspection PyTypeChecker
        downloadResource.putChild(b"events", eventsResource)

        self.platform.addServerResource(b"download", downloadResource)

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
