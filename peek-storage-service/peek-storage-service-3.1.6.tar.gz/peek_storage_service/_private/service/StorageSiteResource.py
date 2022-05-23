from txhttputil.site.BasicResource import BasicResource

from peek_storage_service._private.service.sw_download.PeekSwDownloadResource import (
    PeekSwUpdateDownloadResource,
)
from peek_storage_service._private.service.sw_download.PluginSwDownloadResource import (
    PluginSwDownloadResource,
)

platformSiteRoot = BasicResource()


def setupPlatformSite():
    # Add the platform download resource
    platformSiteRoot.putChild(
        b"platform.sw_install.platform.download", PeekSwUpdateDownloadResource()
    )

    # Add the plugin download resource
    platformSiteRoot.putChild(
        b"platform.sw_install.plugin.download", PluginSwDownloadResource()
    )
