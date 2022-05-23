from abc import ABCMeta

from txhttputil.site.BasicResource import BasicResource


class PeekPlatformAgentHttpHookABC(metaclass=ABCMeta):
    """Peek Agent Service HTTP External API Hook

    The methods provided by this class apply to the HTTP service that provides
    resources (vortex, etc) between the server and the agent, worker and client.

    These resources will not be available to the web apps.

    """

    def __init__(self):
        self.__rootAgentResource = BasicResource()

    def addAgentExternalApiResource(
        self, pluginSubPath: bytes, resource: BasicResource
    ) -> None:
        """Add Agent Resource

        Add a cusotom implementation of a served http resource.

        :param pluginSubPath: The resource path where you want to serve this resource.
        :param resource: The resource to serve.
        :return: None

        """
        pluginSubPath = pluginSubPath.strip(b"/")
        self.__rootAgentResource.putChild(pluginSubPath, resource)

    @property
    def rootAgentResource(self) -> BasicResource:
        """Agent Root Resource

        This returns the root site resource for this plugin.

        """
        return self.__rootAgentResource
