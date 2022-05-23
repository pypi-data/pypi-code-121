import logging

from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy
from vortex.handler.TupleDataObservableProxyHandler import (
    TupleDataObservableProxyHandler,
)

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_eventdb._private.PluginNames import (
    eventdbFilt,
    eventdbObservableName,
    eventdbActionProcessorName,
)
from peek_plugin_eventdb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_eventdb._private.tuples import loadPrivateTuples
from peek_plugin_eventdb.tuples import loadPublicTuples
from txhttputil.downloader.HttpResourceProxy import HttpResourceProxy

logger = logging.getLogger(__name__)


class ClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

    def load(self) -> None:
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("Loaded")

    def start(self):
        # ----------------
        # Proxy actions back to the server, we don't process them at all
        self._loadedObjects.append(
            TupleActionProcessorProxy(
                tupleActionProcessorName=eventdbActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=eventdbFilt,
            )
        )

        # ----------------
        # Provide the devices access to the servers observable
        tupleDataObservableProxyHandler = TupleDataObservableProxyHandler(
            observableName=eventdbObservableName,
            proxyToVortexName=peekServerName,
            additionalFilt=eventdbFilt,
            observerName="Proxy to devices",
        )
        self._loadedObjects.append(tupleDataObservableProxyHandler)

        # Support file downloads for device updates
        # noinspection PyTypeChecker
        proxyResource = HttpResourceProxy(
            self.platform.peekServerHost, self.platform.peekServerHttpPort
        )

        # Matches resource path on server
        # noinspection PyTypeChecker
        self.platform.addOfficeResource(b"download", proxyResource)

        logger.debug("Started")

    def stop(self):
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        logger.debug("Stopped")

    def unload(self):
        logger.debug("Unloaded")
