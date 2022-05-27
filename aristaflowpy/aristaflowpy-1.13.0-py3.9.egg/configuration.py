class Configuration(object):
    def __init__(
        self,
        base_url: str,
        rem_runtime_url: str,
        pimage_renderer_url: str,
        caller_uri: str,
        verify_ssl=True,
        pre_shared_key: str = None,
        application_name: str = None,
        async_thread_pool_size: int = None,
        autostart_timeout_seconds=30,
    ):

        """
        :param base_url
        :param rem_runtime_url
        :param pimage_renderer_url
        """

        if base_url.endswith("/"):
            base_url = base_url[0: len(base_url) - 1]
        if not (base_url.endswith("AristaFlowREST")):
            base_url = base_url + "/AristaFlowREST"

        if rem_runtime_url and str(rem_runtime_url).endswith("/"):
            rem_runtime_url = rem_runtime_url[0: len(rem_runtime_url) - 1]
        if rem_runtime_url and not ('/RuntimeManager/' in str(rem_runtime_url)):
            rem_runtime_url = rem_runtime_url + "/RuntimeManager/RemoteHTMLRuntimeManager"

        if pimage_renderer_url and str(pimage_renderer_url).endswith("/"):
            pimage_renderer_url = pimage_renderer_url[0: len(pimage_renderer_url) - 1]
        if pimage_renderer_url and not ('/ProcessImageRenderer/' in str(pimage_renderer_url)):
            pimage_renderer_url = pimage_renderer_url + "/ProcessImageRenderer/ProcessImageRenderer"

        self.__baseUrl = base_url
        self.__rem_runtime_url = rem_runtime_url
        self.__pimage_renderer_url = pimage_renderer_url
        self.__caller_uri = caller_uri
        self.__verify_ssl = verify_ssl
        self.__pre_shared_key = pre_shared_key
        self.__application_name = application_name
        self.__async_thread_pool_size = async_thread_pool_size
        self.__autostart_timeout_seconds = autostart_timeout_seconds

    @property
    def base_url(self) -> str:
        return self.__baseUrl

    @property
    def rem_runtime_url(self) -> str:
        return self.__rem_runtime_url

    @property
    def pimage_renderer_url(self) -> str:
        return self.__pimage_renderer_url

    @property
    def caller_uri(self) -> str:
        return self.__caller_uri

    @property
    def verify_ssl(self) -> bool:
        return self.__verify_ssl

    @property
    def pre_shared_key(self) -> str:
        return self.__pre_shared_key

    @property
    def application_name(self) -> str:
        return self.__application_name

    @property
    def async_thread_pool_size(self) -> int:
        return self.__async_thread_pool_size

    @property
    def autostart_timeout_seconds(self) -> int:
        return self.__autostart_timeout_seconds

    @property
    def sse_connect_retry_wait(self) -> float:
        """
        Sleep time in seconds between connection retries on lost SSE connections.
        """
        return 5.0

    def get_host(self, service_type: str, service_instance: str = None) -> str:
        """
        Returns the host definition for the given service type / instance, based on the configuration.
        :param service_type: The BPM service type name, e.g. WorklistManager
        :param service_instance: Optionally the simple BPM service instance name, e.g. RemoteHTMLRuntimeManager
        :return: str The host value for the requested service
        """

        if service_instance is None:
            if service_type == "RuntimeManager":
                return self.rem_runtime_url
            elif service_type == "ProcessImageRenderer":
                return self.pimage_renderer_url
            else:
                service_instance = service_type
        return self.base_url + "/" + service_type + "/" + service_instance

    def get_debug(self, service_type: str, service_instance: str = None) -> bool:
        return False
        # return service_type == "RuntimeManager"
