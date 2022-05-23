from pathlib import Path
from typing import Optional

from peek_platform import PeekPlatformConfig
from peek_plugin_base.client.PeekClientPlatformHookABC import PeekClientPlatformHookABC
from peek_plugin_base.client.PeekPlatformOfficeHttpHookABC import (
    PeekPlatformOfficeHttpHookABC,
)
from peek_plugin_base.client.PeekPlatformFieldHttpHookABC import (
    PeekPlatformFieldHttpHookABC,
)


class PeekClientPlatformHook(PeekClientPlatformHookABC):
    @property
    def serviceId(self) -> str:
        import socket

        return "client|" + socket.gethostname()

    def __init__(self, pluginName: str) -> None:
        PeekPlatformFieldHttpHookABC.__init__(self)
        PeekPlatformOfficeHttpHookABC.__init__(self)
        self._pluginName = pluginName

    def getOtherPluginApi(self, pluginName: str) -> Optional[object]:
        pluginLoader = PeekPlatformConfig.pluginLoader

        otherPlugin = pluginLoader.pluginEntryHook(pluginName)
        if not otherPlugin:
            return None

        from peek_plugin_base.client.PluginClientEntryHookABC import (
            PluginClientEntryHookABC,
        )

        assert isinstance(
            otherPlugin, PluginClientEntryHookABC
        ), "Not an instance of PluginClientEntryHookABC"

        return otherPlugin.publishedClientApi

    @property
    def fileStorageDirectory(self) -> Path:
        from peek_platform import PeekPlatformConfig

        return Path(PeekPlatformConfig.config.pluginDataPath(self._pluginName))

    @property
    def peekServerHttpPort(self) -> int:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerHttpPort

    @property
    def peekServerHost(self) -> str:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerHost
