import logging
from typing import Type, Tuple, List

from twisted.internet.defer import inlineCallbacks

from peek_office_service.plugin.ClientFrontendBuildersMixin import (
    ClientFrontendBuildersMixin,
)
from peek_office_service.plugin.PeekClientPlatformHook import PeekClientPlatformHook
from peek_platform.plugin.PluginLoaderABC import PluginLoaderABC
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC

logger = logging.getLogger(__name__)


class ClientPluginLoader(PluginLoaderABC, ClientFrontendBuildersMixin):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert (
            cls._instance is None
        ), "ClientPluginLoader is a singleton, don't construct it"
        cls._instance = PluginLoaderABC.__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        PluginLoaderABC.__init__(self, *args, **kwargs)

    @property
    def _entryHookFuncName(self) -> str:
        return "peekOfficeEntryHook"

    @property
    def _entryHookClassType(self):
        return PluginClientEntryHookABC

    @property
    def _platformServiceNames(self) -> List[str]:
        return ["office"]

    @inlineCallbacks
    def loadOptionalPlugins(self):
        yield PluginLoaderABC.loadOptionalPlugins(self)

        yield from self._buildMobile(self._loadedPlugins.values())

        yield from self._buildDesktop(self._loadedPlugins.values())

        yield from self._buildDocs(self._loadedPlugins.values())

    def unloadPlugin(self, pluginName: str):
        PluginLoaderABC.unloadPlugin(self, pluginName)

        # Remove the Plugin resource tree
        from peek_office_service.backend.SiteRootResource import officeRoot

        try:
            officeRoot.deleteChild(pluginName.encode())
        except KeyError:
            pass

    @inlineCallbacks
    def _loadPluginThrows(
        self,
        pluginName: str,
        EntryHookClass: Type[PluginCommonEntryHookABC],
        pluginRootDir: str,
        requiresService: Tuple[str, ...],
    ) -> PluginCommonEntryHookABC:
        # Everyone gets their own instance of the plugin API
        platformApi = PeekClientPlatformHook(pluginName)

        pluginMain = EntryHookClass(
            pluginName=pluginName, pluginRootDir=pluginRootDir, platform=platformApi
        )

        # Load the plugin
        yield pluginMain.load()

        # Add all the resources required to serve the backend site
        # And all the plugin custom resources it may create
        from peek_office_service.backend.SiteRootResource import officeRoot

        officeRoot.putChild(pluginName.encode(), platformApi.rootOfficeResource)

        self._loadedPlugins[pluginName] = pluginMain
