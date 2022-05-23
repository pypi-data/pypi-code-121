import logging

from celery import Celery
from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import (
    PluginServerStorageEntryHookABC,
)
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import (
    PluginServerWorkerEntryHookABC,
)
from peek_plugin_graphdb._private.server.api.GraphDbApi import GraphDbApi
from peek_plugin_graphdb._private.server.client_handlers.ItemKeyIndexChunkLoadRpc import (
    ItemKeyIndexChunkLoadRpc,
)
from peek_plugin_graphdb._private.server.client_handlers.ItemKeyIndexChunkUpdateHandler import (
    ItemKeyIndexChunkUpdateHandler,
)
from peek_plugin_graphdb._private.server.client_handlers.SegmentChunkIndexUpdateHandler import (
    SegmentChunkIndexUpdateHandler,
)
from peek_plugin_graphdb._private.server.client_handlers.SegmentIndexChunkLoadRpc import (
    SegmentIndexChunkLoadRpc,
)
from peek_plugin_graphdb._private.server.client_handlers.TraceConfigLoadRpc import (
    TraceConfigLoadRpc,
)
from peek_plugin_graphdb._private.server.client_handlers.TraceConfigUpdateHandler import (
    TraceConfigUpdateHandler,
)
from peek_plugin_graphdb._private.server.controller.ImportController import (
    ImportController,
)
from peek_plugin_graphdb._private.server.controller.ItemKeyIndexCompilerQueueController import (
    ItemKeyIndexCompilerQueueController,
)
from peek_plugin_graphdb._private.server.controller.SegmentIndexCompilerQueueController import (
    SegmentIndexCompilerQueueController,
)
from peek_plugin_graphdb._private.server.controller.StatusController import (
    StatusController,
)
from peek_plugin_graphdb._private.storage import DeclarativeBase
from peek_plugin_graphdb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_graphdb._private.storage.Setting import (
    globalSetting,
    SEGMENT_COMPILER_ENABLED,
    ITEM_KEY_COMPILER_ENABLED,
    globalProperties,
)
from peek_plugin_graphdb._private.tuples import loadPrivateTuples
from peek_plugin_graphdb.tuples import loadPublicTuples
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
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
        # Client Handlers and RPC

        self._loadedObjects += SegmentIndexChunkLoadRpc(
            self.dbSessionCreator
        ).makeHandlers()
        self._loadedObjects += TraceConfigLoadRpc(self.dbSessionCreator).makeHandlers()
        self._loadedObjects += ItemKeyIndexChunkLoadRpc(
            self.dbSessionCreator
        ).makeHandlers()

        # ----------------
        # Client Graph Segment client update handler
        clientSegmentChunkUpdateHandler = SegmentChunkIndexUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(clientSegmentChunkUpdateHandler)

        # ----------------
        # ItemKey index client update handler
        itemKeyIndexChunkUpdateHandler = ItemKeyIndexChunkUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(itemKeyIndexChunkUpdateHandler)

        # ----------------
        # Client Search Object client update handler
        clientTraceConfigUpdateHandler = TraceConfigUpdateHandler(self.dbSessionCreator)
        self._loadedObjects.append(clientTraceConfigUpdateHandler)

        # ----------------
        # Queue Status Controller
        statusController = StatusController()
        self._loadedObjects.append(statusController)

        # ----------------
        # Tuple Observable
        tupleObservable = makeTupleDataObservableHandler(
            dbSessionCreator=self.dbSessionCreator,
            segmentStatusController=statusController,
        )
        self._loadedObjects.append(tupleObservable)

        # ----------------
        # Admin Handler
        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        # ----------------
        # Tell the status controller about the Tuple Observable
        statusController.setTupleObservable(tupleObservable)

        # ----------------
        # Main Controller
        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator, tupleObservable=tupleObservable
        )

        self._loadedObjects.append(mainController)

        # ----------------
        # Segment Index Compiler Controller
        segmentIndexCompilerQueueController = SegmentIndexCompilerQueueController(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController,
            clientChunkUpdateHandler=clientSegmentChunkUpdateHandler,
        )
        self._loadedObjects.append(segmentIndexCompilerQueueController)

        # ----------------
        # Key Item Index Compiler Controller
        itemKeyIndexCompilerQueueController = ItemKeyIndexCompilerQueueController(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController,
            clientUpdateHandler=itemKeyIndexChunkUpdateHandler,
        )
        self._loadedObjects.append(itemKeyIndexCompilerQueueController)

        # ----------------
        # Import Controller
        importController = ImportController(clientTraceConfigUpdateHandler)
        self._loadedObjects.append(importController)

        # ----------------
        # Setup the Action Processor
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # ----------------
        # Setup the APIs
        # Initialise the API object that will be shared with other plugins
        self._api = GraphDbApi(importController)
        self._loadedObjects.append(self._api)

        # ----------------
        # Start the compiler controllers

        settings = yield self._loadSettings()

        if settings[SEGMENT_COMPILER_ENABLED]:
            segmentIndexCompilerQueueController.start()

        if settings[ITEM_KEY_COMPILER_ENABLED]:
            itemKeyIndexCompilerQueueController.start()

        # self._test()

        logger.debug("Started")

    def _test(self):
        """Test"""
        # ----------------
        # API test
        # newDocs = []
        # so1 = GraphDbImportSegmentTuple(
        #     key="doc1key",
        #     modelSetKey="testModel",
        #     segmentTypeKey="objectType1",
        #     importGroupHash='test load',
        #     segment={
        #         "name": "134 Ocean Parade, Circuit breaker 1",
        #         "alias": "SO1ALIAS",
        #         "propStr": "Test Property 1",
        #         "propNumArr": [1, 2, 4, 5, 6],
        #         "propStrArr": ["one", "two", "three", "four"]
        #     }
        # )
        #
        # newDocs.append(so1)
        # so2 = GraphDbImportSegmentTuple(
        #     key="doc2key",
        #     modelSetKey="testModel",
        #     segmentTypeKey="objectType2",
        #     importGroupHash='test load',
        #     segment={
        #         "name": "69 Sheep Farmers Rd Sub TX breaker",
        #         "alias": "SO2ALIAS",
        #         "propStr": "Test Property 1",
        #         "propNumArr": [7,8,9,10,11],
        #         "propStrArr": ["five", "siz", "seven", "eight"]
        #     }
        # )
        #
        # newDocs.append(so2)
        #
        # d = Payload(tuples=newDocs).toEncodedPayloadDefer()
        # d.addCallback(self._api.createOrUpdateSegments)
        # d.addErrback(vortexLogFailure, logger, consumeError=True)

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

    ###### Implement PluginServerWorkerEntryHookABC

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
