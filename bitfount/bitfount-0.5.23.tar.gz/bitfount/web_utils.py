"""Utility functions for web interactions."""
import asyncio
from functools import wraps
import inspect
import logging
import time
from typing import (
    Any,
    Awaitable,
    Callable,
    Final,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)

import httpx
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)
import requests
from requests import Response

_logger = logging.getLogger(__name__)

_RETRY_STATUS_CODES: Final = (404, 500, 502, 503, 504)
_DEFAULT_TIMEOUT: Final = 20.0
_DEFAULT_MAX_RETRIES: Final = 3
_DEFAULT_BACKOFF_FACTOR: Final = 1

# These should be replaced with ParamSpec versions once
# https://github.com/python/mypy/issues/11855 is resolved
_SYNC_F = TypeVar("_SYNC_F", bound=Callable[..., Response])
_ASYNC_F = TypeVar("_ASYNC_F", bound=Callable[..., Awaitable[httpx.Response]])
_F = Union[_SYNC_F, _ASYNC_F]


@overload
def _auto_retry_request(
    original_req_func: _SYNC_F,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = _DEFAULT_BACKOFF_FACTOR,
) -> _SYNC_F:
    ...


@overload
def _auto_retry_request(
    original_req_func: _ASYNC_F,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = _DEFAULT_BACKOFF_FACTOR,
) -> _ASYNC_F:
    ...


@overload
def _auto_retry_request(
    original_req_func: None = None,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = _DEFAULT_BACKOFF_FACTOR,
) -> Callable[[_F], _F]:
    ...


def _auto_retry_request(
    original_req_func: Optional[_F] = None,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = _DEFAULT_BACKOFF_FACTOR,
) -> Union[_F, Callable[[_F], _F]]:
    """Applies automatic retries to HTTP requests when encountering specific errors.

    Wraps the target `requests` call in a retry mechanism which will reattempt
    the call if:
        - A connection error occurs
        - A retryable HTTP error response is received

    Utilises an exponential backoff to avoid flooding the request and to give
    time for the issue to resolve itself.

    Can be used as either an argumentless decorator (@_auto_retry_request) or a
    decorator with args (@_auto_retry_request(...)).
    """

    def _decorate(req_func: _F) -> _F:
        """Apply decoration to target request function."""
        if inspect.iscoroutinefunction(req_func):
            return _get_async_wrapper(req_func, max_retries, backoff_factor)
        else:
            return _get_sync_wrapper(req_func, max_retries, backoff_factor)

    if original_req_func:
        # Was used as @_auto_retry_dec (or called directly).
        # original_req_func was passed in through the decorator machinery so just
        # wrap and return.
        return _decorate(original_req_func)
    else:
        # Was used as @_auto_retry_dec(**kwargs).
        # original_req_func not yet passed in so need to return a decorator function
        # to allow the decorator machinery to pass it in.
        return _decorate


def _get_sync_wrapper(
    req_func: _SYNC_F, max_retries: int, backoff_factor: int
) -> _SYNC_F:
    @wraps(req_func)
    def _wrapped_sync_req_func(*args: Any, **kwargs: Any) -> Response:
        """Wraps target request function in retry capability.

        Adds automatic retry, backoff, and logging.
        """
        # Set default timeout if one not provided
        timeout = kwargs.get("timeout", None)
        if timeout is None:
            logging.debug(
                f"No request timeout provided,"
                f" setting to default timeout ({_DEFAULT_TIMEOUT}s)"
            )
            kwargs["timeout"] = _DEFAULT_TIMEOUT

        retry_count = 0

        while retry_count <= max_retries:
            final_retry = retry_count == max_retries

            # Attempt to make wrapped request and handle if it doesn't work
            # as expected
            try:
                resp: Response = req_func(*args, **kwargs)

                # Check, if response received but not successful, that it is a
                # status code we are willing to retry and we have retries left
                if resp.status_code not in _RETRY_STATUS_CODES or final_retry:
                    return resp
                else:
                    failure_cause_msg = (
                        f"Error ({resp.status_code}) for"
                        f" {resp.request.method}:{resp.url}"
                    )
            except requests.ConnectionError as ex:
                # If a connection error occurs, we can retry unless
                # this is our final attempt
                if final_retry:
                    raise ex
                else:
                    # If the exception contains request info, we can use it
                    if req := ex.request:
                        failure_cause_msg = (
                            f"Connection error ({str(ex)}) for"
                            f" {req.method}:{req.url}"
                        )
                    else:
                        failure_cause_msg = f"Connection error ({str(ex)})"

            # If we reach this point we must be attempting a retry
            retry_count += 1

            # Backoff is increased using standard exponential backoff formula
            # For standard backoff factor of one this results in backoffs of
            # [1, 2, 4, 8, ...] seconds.
            backoff = backoff_factor * (2 ** (retry_count - 1))

            # Log out failure information and retry information.
            _logger.debug(
                f"{failure_cause_msg}; "
                f"will retry in {backoff} seconds (attempt {retry_count})."
            )

            time.sleep(backoff)

        # We shouldn't reach this point due to how the loop can be exited,
        # but just in case
        raise requests.ConnectionError(
            "Unable to make connection, even after multiple attempts."
        )

    return cast(_SYNC_F, _wrapped_sync_req_func)


def _get_async_wrapper(
    req_func: _ASYNC_F, max_retries: int, backoff_factor: int
) -> _ASYNC_F:
    @wraps(req_func)
    async def _wrapped_async_req_func(*args: Any, **kwargs: Any) -> httpx.Response:
        """Wraps target HTTPX request function in retry capability.

        Adds automatic retry, backoff, and logging.
        """
        # Set default timeout if one not provided
        timeout = kwargs.get("timeout", None)
        if timeout is None or timeout is USE_CLIENT_DEFAULT:
            logging.debug(
                f"No request timeout provided,"
                f" setting to default timeout ({_DEFAULT_TIMEOUT}s)"
            )
            kwargs["timeout"] = _DEFAULT_TIMEOUT

        retry_count = 0

        while retry_count <= max_retries:
            final_retry = retry_count == max_retries

            # Attempt to make wrapped request and handle if it doesn't work
            # as expected
            try:
                resp: httpx.Response = await req_func(*args, **kwargs)

                # Check, if response received but not successful, that it is a
                # status code we are willing to retry and we have retries left
                if resp.status_code not in _RETRY_STATUS_CODES or final_retry:
                    return resp
                else:
                    failure_cause_msg = (
                        f"Error ({resp.status_code}) for"
                        f" {resp.request.method}:{resp.url}"
                    )
            except httpx.ConnectError as ex:
                # If a connection error occurs, we can retry unless
                # this is our final attempt
                if final_retry:
                    raise ex
                else:
                    # If the exception contains request info, we can use it
                    try:
                        req = ex.request
                    except RuntimeError:
                        failure_cause_msg = f"Connection error ({str(ex)})"
                    else:
                        failure_cause_msg = (
                            f"Connection error ({str(ex)}) for"
                            f" {req.method}:{req.url}"
                        )

            # If we reach this point we must be attempting a retry
            retry_count += 1

            # Backoff is increased using standard exponential backoff formula
            # For standard backoff factor of one this results in backoffs of
            # [1, 2, 4, 8, ...] seconds.
            backoff = backoff_factor * (2 ** (retry_count - 1))

            # Log out failure information and retry information.
            _logger.debug(
                f"{failure_cause_msg}; "
                f"will retry in {backoff} seconds (attempt {retry_count})."
            )

            await asyncio.sleep(backoff)

        # We shouldn't reach this point due to how the loop can be exited,
        # but just in case
        raise httpx.HTTPError(
            "Unable to make connection, even after multiple attempts."
        )

    return cast(_ASYNC_F, _wrapped_async_req_func)


# Create patched versions of the `requests` methods
request = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.request
)
head = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.head
)
get = _auto_retry_request(requests.get)  #: This is needed to get pdoc to pick these up
post = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.post
)
put = _auto_retry_request(requests.put)  #: This is needed to get pdoc to pick these up
patch = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.patch
)
delete = _auto_retry_request(  #: This is needed to get pdoc to pick these up
    requests.delete
)

__pdoc__ = {
    "request": "See `requests.request()` for more details.",
    "head": "See `requests.head()` for more details.",
    "get": "See `requests.get()` for more details.",
    "post": "See `requests.post()` for more details.",
    "put": "See `requests.put()` for more details.",
    "patch": "See `requests.patch()` for more details.",
    "delete": "See `requests.delete()` for more details.",
}


# Create patched versions of the HTTPX methods
class _AsyncClient(httpx.AsyncClient):
    # We only wrap this method in _auto_retry_request as any calls to the others
    # (post, get, etc) will make use of this. Wrapping them all would result in
    # a double retry loop, but we can't _not_ wrap request as it is often used
    # directly.
    @_auto_retry_request
    async def request(
        self,
        method: str,
        url: URLTypes,
        *,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[dict] = None,
    ) -> httpx.Response:
        """See httpx.AsyncClient.request() for information."""  # noqa: D402
        return await super().request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_request(
    method: str,
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.request() for more information."""
    async with _AsyncClient() as client:
        return await client.request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_get(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.get() for more information."""
    async with _AsyncClient() as client:
        return await client.get(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_options(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.options() for more information."""
    async with _AsyncClient() as client:
        return await client.options(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_head(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.head() for more information."""
    async with _AsyncClient() as client:
        return await client.head(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_post(
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.post() for more information."""
    async with _AsyncClient() as client:
        return await client.post(
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_put(
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.put() for more information."""
    async with _AsyncClient() as client:
        return await client.put(
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_patch(
    url: URLTypes,
    *,
    content: Optional[RequestContent] = None,
    data: Optional[RequestData] = None,
    files: Optional[RequestFiles] = None,
    json: Optional[Any] = None,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.patch() for more information."""
    async with _AsyncClient() as client:
        return await client.patch(
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


async def async_delete(
    url: URLTypes,
    *,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
    cookies: Optional[CookieTypes] = None,
    auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: Optional[dict] = None,
) -> httpx.Response:
    """See httpx.delete() for more information."""
    async with _AsyncClient() as client:
        return await client.delete(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )
