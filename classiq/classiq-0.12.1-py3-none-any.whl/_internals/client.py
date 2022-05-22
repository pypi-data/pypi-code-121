import functools
import inspect
import logging
import os
import platform
import ssl
import sys
import urllib.parse
from typing import Any, Awaitable, Callable, Dict, NoReturn, Optional, Union

import httpx
import pydantic
import websockets.client
from semver import VersionInfo

from classiq.interface import __version__ as classiq_interface_version
from classiq.interface.server import authentication
from classiq.interface.server.routes import ROUTE_PREFIX

from classiq._internals import config
from classiq._internals.authentication import token_manager
from classiq._version import VERSION as CLASSIQ_VERSION
from classiq.exceptions import ClassiqAPIError, ClassiqExpiredTokenError

_VERSION_UPDATE_SUGGESTION = (
    'Run "pip install -U <PACKAGE>==<REQUIRED VERSION>" to resolve the conflict.'
)
_FRONTEND_VARIANT: str = "classiq-sdk"
_INTERFACE_VARIANT: str = "classiq-interface-sdk"
_USERAGENT_SEPARATOR: str = " "

_logger = logging.getLogger(__name__)

_RETRY_COUNT = 2


@functools.lru_cache()
def _get_python_execution_environment() -> str:
    # Try spyder
    if any("SPYDER" in name for name in os.environ):
        return "Spyder"

    # try ipython and its variants
    try:
        shell = get_ipython().__class__.__name__  # type: ignore[name-defined]
        if shell == "ZMQInteractiveShell":
            return "Jupyter"  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return "IPython"  # Terminal running IPython
        else:
            return "IPython-other"  # Other type (?)
    except NameError:
        pass  # Probably standard Python interpreter

    # Try VSCode
    if "debugpy" in sys.modules:
        return "VSCode"

    # Try pycharm
    if "PYCHARM_HOSTED" in os.environ:
        return "PyCharm"

    return "Python"


@functools.lru_cache()
def _get_user_agent_header() -> Dict[str, str]:
    python_version = (
        f"python({_get_python_execution_environment()})/{platform.python_version()}"
    )
    os_platform = f"{os.name}/{platform.platform()}"
    frontend_version = f"{_FRONTEND_VARIANT}/{CLASSIQ_VERSION}"
    interface_version = f"{_INTERFACE_VARIANT}/{classiq_interface_version}"
    return {
        "User-Agent": _USERAGENT_SEPARATOR.join(
            (python_version, os_platform, frontend_version, interface_version)
        )
    }


def refresh_token_on_failure(func: Callable[..., Awaitable[Any]]):
    if not inspect.iscoroutinefunction(func):
        raise TypeError("Must decorate a coroutine function")

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        for i in range(_RETRY_COUNT):
            try:
                return await func(*args, **kwargs)
            except ClassiqExpiredTokenError:
                _logger.info(
                    "Token expired when trying to %s with args %s %s",
                    func,
                    args,
                    kwargs,
                    exc_info=True,
                )
                if i == _RETRY_COUNT - 1:
                    raise
                await client().update_expired_access_token()

    return wrapper


class HostVersions(pydantic.BaseModel):
    classiq_interface: pydantic.StrictStr = pydantic.Field()


class Client:
    _UNKNOWN_VERSION = "0.0.0"

    def __init__(self, conf: config.Configuration):
        self._config = conf
        self._token_manager = token_manager.TokenManager()
        self._ssl_context = ssl.create_default_context()
        self._HTTP_TIMEOUT_SECONDS = (
            3600  # Needs to be synced with load-balancer timeout
        )

    @classmethod
    def _handle_response(cls, response: httpx.Response) -> Union[Dict, str]:
        if response.is_error:
            cls.handle_error(response)
        return response.json()

    @staticmethod
    def handle_error(response: httpx.Response) -> NoReturn:
        expired = (
            response.status_code == httpx.codes.UNAUTHORIZED
            and response.json()["detail"] == authentication.EXPIRED_TOKEN_ERROR
        )

        if expired:
            raise ClassiqExpiredTokenError("Expired token.")

        message = f"Call to API failed with code {response.status_code}"
        try:
            detail = response.json()["detail"]
            message += f": {detail}"
        except Exception:  # nosec B110
            pass
        raise ClassiqAPIError(message)

    def _make_client_args(self) -> Dict[str, Any]:
        return {
            "base_url": self._config.host,
            "timeout": self._HTTP_TIMEOUT_SECONDS,
            "headers": {
                **self._get_authorization_header(),
                **_get_user_agent_header(),
            },
        }

    @refresh_token_on_failure
    async def call_api(
        self, http_method: str, url: str, body: Optional[Dict] = None
    ) -> Union[Dict, str]:
        async with self.async_client() as async_client:
            response = await async_client.request(
                method=http_method, url=url, json=body
            )
            return self._handle_response(response)

    def sync_call_api(
        self, http_method: str, url: str, body: Optional[Dict] = None
    ) -> Union[Dict, str]:
        with httpx.Client(**self._make_client_args()) as sync_client:
            response = sync_client.request(method=http_method, url=url, json=body)
            return self._handle_response(response)

    def async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(**self._make_client_args())

    def _get_authorization_header(self) -> Dict[str, str]:
        access_token = self._token_manager.get_access_token()
        if access_token is None:
            return dict()
        return {"Authorization": f"Bearer {access_token}"}

    def _get_authorization_query_string(self) -> str:
        access_token = self._token_manager.get_access_token()
        if access_token is None:
            return ""
        return urllib.parse.urlencode({"token": access_token})

    async def update_expired_access_token(self) -> None:
        await self._token_manager.update_expired_access_token()

    def establish_websocket_connection(
        self, path: str, **kwargs
    ) -> websockets.client.connect:
        _MAX_PAYLOAD_SIZE = 2**23  # = 8MiB ~= 8MB
        max_size = kwargs.get("max_size", _MAX_PAYLOAD_SIZE)
        ping_interval = kwargs.get("ping_interval", None)
        url = urllib.parse.urlsplit(self._config.ws_uri)
        url = url._replace(path=path, query=self._get_authorization_query_string())

        return websockets.client.connect(
            uri=url.geturl(),
            ssl=self._ssl_context if self._config.ws_uri.scheme == "wss" else None,
            max_size=max_size,
            ping_interval=ping_interval,
            extra_headers=_get_user_agent_header(),
        )

    def get_backend_uri(self) -> str:
        return self._config.host

    def _get_host_version(self) -> str:
        host = HostVersions.parse_obj(
            self.sync_call_api("get", f"{ROUTE_PREFIX}/versions")
        )
        return host.classiq_interface

    @classmethod
    def _check_matching_versions(
        cls, lhs_version: str, rhs_version: str, normalize: bool = True
    ) -> bool:
        if lhs_version == cls._UNKNOWN_VERSION or rhs_version == cls._UNKNOWN_VERSION:
            # In case one of those versions is unknown, they are considered equal
            _logger.debug(
                "Either {} or {} is an unknown version. Assuming both versions are equal.",
                lhs_version,
                rhs_version,
            )
            return True
        if not normalize:
            return lhs_version == rhs_version
        processed_lhs = VersionInfo.parse(lhs_version)
        processed_rhs = VersionInfo.parse(rhs_version)
        return processed_lhs.to_tuple()[:2] == processed_rhs.to_tuple()[:2]

    def check_host(self) -> None:
        # This function is NOT async (despite the fact that it can be) because it's called from a non-async context.
        # If this happens when we already run in an event loop (e.g. inside a call to asyncio.run), we can't go in to
        # an async context again.
        # Since this function should be called ONCE in each session, we can handle the "cost" of blocking the
        # event loop.
        if not self._check_matching_versions(
            classiq_interface_version, CLASSIQ_VERSION, normalize=False
        ):
            # When raising an exception, use the original strings
            raise ClassiqAPIError(
                f"Classiq API version mismatch: 'classiq' version is {CLASSIQ_VERSION}, "
                f"'classiq-interface' version is {classiq_interface_version}. {_VERSION_UPDATE_SUGGESTION}"
            )

        try:
            raw_host_version = self._get_host_version()
        except httpx.ConnectError:
            _logger.warning(
                "Version check failed - host unavailable.",
            )
        else:
            if not self._check_matching_versions(
                raw_host_version, classiq_interface_version
            ):
                raise ClassiqAPIError(
                    f"Classiq API version mismatch: 'classiq-interface' version is "
                    f"{classiq_interface_version}, backend version is {raw_host_version}. {_VERSION_UPDATE_SUGGESTION}"
                )

    async def authenticate(self, overwrite: bool) -> None:
        await self._token_manager.manual_authentication(overwrite=overwrite)


DEFAULT_CLIENT: Optional[Client] = None


def client() -> Client:
    global DEFAULT_CLIENT
    if DEFAULT_CLIENT is None:
        # This call initializes DEFAULT_CLIENT
        configure(config.init())
    assert DEFAULT_CLIENT is not None
    return DEFAULT_CLIENT


def configure(conf: config.Configuration) -> None:
    global DEFAULT_CLIENT
    assert DEFAULT_CLIENT is None, "Can not configure client after first usage."

    DEFAULT_CLIENT = Client(conf=conf)
    if conf.should_check_host:
        DEFAULT_CLIENT.check_host()
