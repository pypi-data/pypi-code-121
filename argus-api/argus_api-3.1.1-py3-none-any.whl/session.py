import os

from typing import Optional, List, Union, TYPE_CHECKING, Collection

from requests.sessions import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


from argus_api._validators import validate_http_response
from argus_api.exceptions.client import ArgusAPIAuthenticationError
from argus_api.authentication import ArgusAPIAuth, APIKeyAuth, get_auth_from_cli_config
from argus_api.utils import _load_cli_settings

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

if TYPE_CHECKING:
    from requests import Response

# URL of the Argus API
ARGUS_API_URL = "https://api.mnemonic.no"
# URL of the development Argus API
ARGUS_DEV_API_URL = "https://devapi.mnemonic.no"


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, timeout=30, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


package_version = version("argus-api")


class ArgusAPISession:

    SUPPORTED_METHODS = ("get", "post", "put", "delete")
    USER_AGENT = f"ArgusAPI/{package_version}"
    TIMEOUT_ENV_VAR = "ARGUS_API_TIMEOUT"
    DEFAULT_TIMEOUT = 30

    # instance attributes
    #: authentication configuration of the session
    auth: ArgusAPIAuth
    #: API base URL. Should not contain a trailing ``/``.
    base_url: str
    #: proxies dictionary as expected by the ``proxies`` argument of
    #: :func:`requests.request`
    proxies: dict
    #: SSL certify verification setting as expected by the ``verify`` argument
    #: of :func:`requests.request`
    verify: Union[bool, str]
    #: Used to calculate sleep time between retries. backoff sleep time formula:
    #: {backoff factor} * (2 ** ({number of total retries} - 1))
    backoff_factor: int

    auth: "ArgusAPIAuth"
    authenticated: bool

    def __init__(
        self,
        auth: Optional[Union["ArgusAPIAuth", str]] = None,
        api_url: Optional[str] = None,
        use_cli_config: bool = False,
        verify: Union[bool, str] = True,
        proxies: Optional[dict] = None,
        dev: bool = False,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = 3,
        retry_methods: Collection[int] = ("GET", "PUT", "DELETE", "POST"),
        retry_statuses: Collection[int] = (500, 503, 504),
        retry_backoff_factor: Union[int, float] = 0,
    ):
        """Initialize an API session.

        :param auth: authentication settings as an
          :class:`~argus_api.authentication.ArgusAPIAuth` object. can be let unspecified
          if the ``use_cli_config`` argument is `True`. An API key can also be provided as
          a string.
        :param api_url: base URL of the Argus API. If not set, the default API URL will
          be used.
        :param use_cli_config: if set, default configuration will be loaded from the
          ``argus-cli`` configuration file.
        :param verify: SSL certificate verification. Can be set to a boolean or the
          path to a CA certificate bundle.
        :param proxies: proxies dictionary as expected by the ``proxies`` argument of
           :func:`requests.request`
        :param dev: if set to `True`, use the development API server. Will take
          precedence over the ``api_url`` argument.
        :param timeout: default client-side timeout (in seconds).
        :param max_retries: maximum number of retries on failed requests.
        :param retry_statuses: HTTP status codes on which to retry.
        :param retry_backoff_factor: "backoff factor" between automatic retries.
        """
        self.user_agent = self.USER_AGENT
        self.use_cli_config = False
        if use_cli_config:
            self.use_cli_config = True
            settings = _load_cli_settings()
            cli_api_settings = settings.get("api", {})

        self.base_url = api_url
        if self.base_url is None:
            if dev:
                self.base_url = ARGUS_DEV_API_URL
            elif use_cli_config:
                self.base_url = cli_api_settings.get("api_url", ARGUS_API_URL)
            else:
                self.base_url = ARGUS_API_URL

        self._session = Session()

        # set default timeout and retry strategy
        self.default_timeout = -1
        self.default_timeout = self._get_timeout() if timeout is None else timeout

        self.max_retries = max_retries
        self.retry_statuses = retry_statuses
        self.retry_methods = retry_methods
        self.backoff_factor = retry_backoff_factor

        self.set_adapter()

        # set proxies
        if proxies is not None:
            self.proxies = proxies

        # set headers
        self._session.headers.update(
            {"User-Agent": self.USER_AGENT, "content": "application/json"}
        )

        self.authenticated = False
        self._auth_from_cli_config = False
        if auth:
            if isinstance(auth, str):
                self._auth = APIKeyAuth(api_key=auth)
            else:
                self._auth = auth
        elif use_cli_config:
            self._auth = get_auth_from_cli_config()
            self._auth_from_cli_config = True
        else:
            raise ArgusAPIAuthenticationError(
                "No authentication was provided to the session."
            )

        self._verify = None
        self.verify = verify

    def __enter__(self):
        self.__previous_session = get_session()
        set_session(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_session(self.__previous_session)

    @property
    def auth(self) -> ArgusAPIAuth:
        return self._auth

    @auth.setter
    def auth(self, value):
        self._auth.cleanup_session(self)
        self.authenticated = False
        self._auth = value

    @property
    def proxies(self):
        return self._session.proxies

    @proxies.setter
    def proxies(self, value):
        self._session.proxies = value

    @property
    def verify(self):
        return self._session.verify

    @verify.setter
    def verify(self, value):
        self._verify = value
        self._session.verify = value

    def _get_timeout(self) -> int:
        timeout = int(os.getenv(self.TIMEOUT_ENV_VAR, -1))
        # the default depends on whether we are calling this to initialize it
        # for the first time.
        default_timeout = (
            self.default_timeout if self.default_timeout >= 0 else self.DEFAULT_TIMEOUT
        )
        if timeout < 0:
            if self.use_cli_config:
                settings = _load_cli_settings()
                timeout = settings.get("api", {}).get("timeout", default_timeout)
            else:
                timeout = default_timeout
        return timeout

    def set_timeout(self, timeout: int):
        """Sets the default timeout for the session

        :param timeout: new default timeout in seconds
        """
        self.set_adapter(default_timeout=timeout)

    def set_adapter(
        self,
        default_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_statuses: Optional[List[int]] = None,
        retry_methods: Optional[List[str]] = None,
        backoff_factor: Optional[Union[int, float]] = None,
    ):
        """Sets the HTTP adapter for the session

        this controls global timeout and retry settings.

        :param default_timeout: default timeout in seconds
        :param max_retries: maximun retries on failures
        :param retry_statuses: HTTP status codes on which to retry
        :param retry_methods: whitelist of methods for which retries will be performed
        :param backoff_factor: factor for incremental retry delays
        """
        self.default_timeout = default_timeout or self.default_timeout
        self.max_retries = max_retries or self.max_retries
        self.retry_statuses = retry_statuses or self.retry_statuses
        self.retry_methods = retry_methods or self.retry_methods
        self.backoff_factor = backoff_factor or self.backoff_factor

        self.retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=self.retry_statuses,
            allowed_methods=self.retry_methods,
            raise_on_redirect=False,
            backoff_factor=self.backoff_factor,
            raise_on_status=False,
        )
        adapter = TimeoutHTTPAdapter(
            timeout=self.default_timeout, max_retries=self.retry_strategy
        )
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _refresh_auth_from_settings(self):
        current_auth_settings = get_auth_from_cli_config()
        if current_auth_settings != self.auth:
            # auth settings have changed, we need to refresh
            self.auth.cleanup_session(self)
            self.auth = current_auth_settings

    def _request(self, method, _route, *args, **kwargs) -> "Response":
        """

        _route should have a leading /
        """

        # build destination URL
        base_url = self.base_url
        if kwargs.get("server_url"):
            base_url = kwargs["server_url"]
        url = f"{base_url}{_route}"

        # allow auth header override
        headers_override = {}
        if kwargs.get("apiKey"):
            headers_override["Argus-Api-Key"] = kwargs["apiKey"]
        elif kwargs.get("authentication"):
            authentication = kwargs["authentication"]
            if isinstance(authentication, dict):
                headers_override["Argus-Api-Key"] = None
                headers_override.update(authentication)
            elif isinstance(authentication, ArgusAPIAuth):
                if not authentication.is_authenticated:
                    authentication.authenticate(self.base_url)
                if authentication.headers:
                    headers_override.update(authentication(url))
                if authentication.cookies:
                    cookies = kwargs.get("cookies", {})
                    cookies.update(authentication.cookies)
                    kwargs["cookies"] = cookies
            elif callable(authentication):
                headers_override["Argus-Api-Key"] = None
                headers_override.update(authentication(url))

        else:  # no override, use the session's auth object
            if self._auth_from_cli_config:
                # settings are changed at runtime, we need to re-check them
                self._refresh_auth_from_settings()
            if not self.authenticated:
                self.auth.authenticate_session(self)

        timeout = self._get_timeout()

        if "timeout" not in kwargs and timeout != self.default_timeout:
            kwargs["timeout"] = timeout

        # update request-specific headers
        if headers_override:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"].update(headers_override)

        # remove proxies from the args if not set to avoid overriding the
        # session-level proxies
        if "proxies" in kwargs and kwargs["proxies"] is None:
            del kwargs["proxies"]
        # same with verify
        if "verify" in kwargs and kwargs["verify"] is None:
            del kwargs["verify"]

        # clean kwargs before passing them down to requests
        for arg in ("apiKey", "authentication", "server_url"):
            if arg in kwargs:
                del kwargs[arg]

        # perform the request
        response = getattr(self._session, method)(url, *args, **kwargs)

        # check the status code for errors
        validate_http_response(response)

        return response

    def get(self, _route, *args, **kwargs):
        return self._request("get", _route, *args, **kwargs)

    def post(self, _route, *args, **kwargs):
        return self._request("post", _route, *args, **kwargs)

    def put(self, _route, *args, **kwargs):
        return self._request("put", _route, *args, **kwargs)

    def delete(self, _route, *args, **kwargs):
        return self._request("delete", _route, *args, **kwargs)


class SessionManager(object):
    """Singleton holding the current global session."""
    _instance = None
    session: "ArgusAPISession"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._session = ArgusAPISession(auth=ArgusAPIAuth())
        return cls._instance

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session: ArgusAPISession):
        self._session = session


def get_session() -> ArgusAPISession:
    """Get the session currently used by ``argus_api.lib`` methods."""
    return SessionManager().session


def set_session(session: ArgusAPISession):
    """Set the session used by ``argus_api.lib`` methods.

    :param session: session to use.
    """
    SessionManager().session = session

# this is not be used, except by argus_api.api methods. meant ONLY for these to retain
# argus_api.api's legacy behavior.
_legacy_session = ArgusAPISession(use_cli_config=True)
