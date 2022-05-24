import asyncio
import functools
import os
import socket
import sys
from typing import Any

import click
from urllib3.connection import HTTPConnection
import wrapt

import anyscale.client.openapi_client as openapi_client
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
import anyscale.sdk.anyscale_client as anyscale_client
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as AnyscaleApi
from anyscale.sdk.anyscale_client.rest import ApiException as ApiExceptionExternal
from anyscale.shared_anyscale_utils.headers import RequestHeaders
from anyscale.version import __version__ as version


# NOTE: Some OSes don't implement all of these, so only include those that the OS supports.
_SOCKET_OPTIONS = (
    HTTPConnection.default_socket_options
    + [
        (getattr(socket, t[0]), getattr(socket, t[1]), t[2])
        for t in [
            ("SOL_SOCKET", "SO_KEEPALIVE", 1),
            # Begin sending keepalives after 15 seconds of no activity:
            ("SOL_TCP", "TCP_KEEPIDLE", 15),
            # Send keepalives every 15 seconds:
            ("SOL_TCP", "TCP_KEEPINTVL", 15),
            # Number failed keepalives before marking the connection as dead:
            ("SOL_TCP", "TCP_KEEPCNT", 6),
        ]
        if hasattr(socket, t[0]) and hasattr(socket, t[1])
    ]
    # Darwin uses TCP_KEEPALIVE[A] instead of TCP_KEEPIDLE. Unfortunatley, this was
    # only added to the socket library recently (June 2021)[B], so we include the value
    # of TCP_KEEPALIVE (16)[C] if the version of python is not super recent.
    # [A] Bug: https://bugs.python.org/issue34932
    # [B] Resolution: https://github.com/python/cpython/pull/25079
    # [C] Darwin Source: https://github.com/apple/darwin-xnu/blob/main/bsd/netinet/tcp.h
    + (
        [(6, getattr(socket, "TCP_KEEPALIVE", 16), 15)]
        if sys.platform == "darwin"
        else []
    )
)


# client is of type APIClient, which is auto-generated
def configure_tcp_keepalive(client: Any) -> None:
    assert hasattr(
        client, "rest_client"
    ), f"Incorrect object of type: {type(client)}\nThis object does not have a `rest_client` property."
    client.rest_client.pool_manager.connection_pool_kw[
        "socket_options"
    ] = _SOCKET_OPTIONS


# client is of type APIClient, which is auto-generated
def configure_open_api_client_headers(client: Any, client_name: str) -> None:
    client.set_default_header(RequestHeaders.CLIENT, client_name)
    client.set_default_header(RequestHeaders.CLIENT_VERSION, version)


class _ApiClient(object):
    api_client: DefaultApi = None
    anyscale_client: AnyscaleApi = None


def format_api_exception(
    e, method: str, resource_path: str, raise_structured_exception: bool = False,
) -> None:
    if os.environ.get("ANYSCALE_DEBUG") == "1" or raise_structured_exception:
        raise e
    else:
        raise click.ClickException(
            f"API Exception ({e.status}) from {method} {resource_path} \n"
            f"Reason: {e.reason}\nHTTP response body: {e.body}\n"
            f"Trace ID: {e.headers._container.get('x-trace-id', None)}"
        )


class ApiClientWrapperInternal(openapi_client.ApiClient):
    def __init__(self, *args, raise_structured_exception: bool = False, **kwargs):
        """
        Arguments:
            raise_structured_exception (bool): If True, API exceptions will be raised
            as structured exceptions. If this and ANYSCALE_DEBUG are False, API
            exceptions will be raised as user friendly but unstructured Click exceptions.
            This arguement allows us to determine the type of raised error in code, but
            users should ANYSCALE_DEBUG to configure this.
        """
        self.raise_structured_exception = raise_structured_exception
        super().__init__(*args, **kwargs)

    def call_api(
        self,
        resource_path,
        method,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        post_params=None,
        files=None,
        response_type=None,
        auth_settings=None,
        async_req=None,
        _return_http_data_only=None,
        collection_formats=None,
        _preload_content=True,
        _request_timeout=None,
        _host=None,
    ):
        try:
            return openapi_client.ApiClient.call_api(
                self,
                resource_path,
                method,
                path_params,
                query_params,
                header_params,
                body,
                post_params,
                files,
                response_type,
                auth_settings,
                async_req,
                _return_http_data_only,
                collection_formats,
                _preload_content,
                _request_timeout,
                _host,
            )
        except ApiExceptionInternal as e:
            format_api_exception(
                e, method, resource_path, self.raise_structured_exception
            )


class ApiClientWrapperExternal(anyscale_client.ApiClient):
    def __init__(self, *args, raise_structured_exception: bool = False, **kwargs):
        """
        Arguments:
            raise_structured_exception (bool): If True, API exceptions will be raised
            as structured exceptions. If this and ANYSCALE_DEBUG are False, API
            exceptions will be raised as user friendly but unstructured Click exceptions.
            This arguement allows us to determine the type of raised error in code, but
            users should ANYSCALE_DEBUG to configure this.
        """
        self.raise_structured_exception = raise_structured_exception
        super().__init__(*args, **kwargs)

    def call_api(
        self,
        resource_path,
        method,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        post_params=None,
        files=None,
        response_type=None,
        auth_settings=None,
        async_req=None,
        _return_http_data_only=None,
        collection_formats=None,
        _preload_content=True,
        _request_timeout=None,
        _host=None,
    ):
        try:
            return anyscale_client.ApiClient.call_api(
                self,
                resource_path,
                method,
                path_params,
                query_params,
                header_params,
                body,
                post_params,
                files,
                response_type,
                auth_settings,
                async_req,
                _return_http_data_only,
                collection_formats,
                _preload_content,
                _request_timeout,
                _host,
            )
        except ApiExceptionExternal as e:
            format_api_exception(
                e, method, resource_path, self.raise_structured_exception
            )


@wrapt.decorator
def make_async(_func, instance, args, kwargs):
    loop = asyncio.get_event_loop()
    func = functools.partial(_func, *args, **kwargs)
    return loop.run_in_executor(executor=None, func=func)


class AsyncApiClientWrapperExternal(ApiClientWrapperExternal):
    @make_async
    def call_api(self, *args, **kwargs):
        return super().call_api(*args, **kwargs)


_api_client = _ApiClient()
