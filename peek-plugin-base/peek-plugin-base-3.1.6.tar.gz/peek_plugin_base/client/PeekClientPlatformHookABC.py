from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFileStorageHookABC import (
    PeekPlatformFileStorageHookABC,
)
from peek_plugin_base.PeekPlatformServerInfoHookABC import PeekPlatformServerInfoHookABC
from peek_plugin_base.client.PeekPlatformOfficeHttpHookABC import (
    PeekPlatformOfficeHttpHookABC,
)
from peek_plugin_base.client.PeekPlatformFieldHttpHookABC import (
    PeekPlatformFieldHttpHookABC,
)


class PeekClientPlatformHookABC(
    PeekPlatformCommonHookABC,
    PeekPlatformFieldHttpHookABC,
    PeekPlatformOfficeHttpHookABC,
    PeekPlatformServerInfoHookABC,
    PeekPlatformFileStorageHookABC,
):
    pass
