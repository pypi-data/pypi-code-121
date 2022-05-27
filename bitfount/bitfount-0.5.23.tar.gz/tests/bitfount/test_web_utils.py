"""Tests for the web utility functions."""
from functools import partial
import http
import logging
import re
from typing import Any, Awaitable, Callable, Final, Optional, TypedDict, cast
from unittest.mock import AsyncMock, Mock, PropertyMock, call

from _pytest.logging import LogCaptureFixture
import httpx
import pytest
from pytest import fixture
from pytest_httpx import HTTPXMock
from pytest_mock import MockerFixture
import requests
from requests import Response
import responses
from typing_extensions import NotRequired

from bitfount import web_utils
from bitfount.web_utils import _auto_retry_request
from tests.utils import PytestRequest
from tests.utils.helper import get_debug_logs, unit_test

_HTTP_STATUS_CODES: Final = tuple(i.value for i in http.HTTPStatus)
_HTTP_CALL_TYPES: Final = (
    "request-head",
    "request-get",
    "request-post",
    "request-put",
    "request-patch",
    "request-delete",
    "head",
    "get",
    "post",
    "put",
    "patch",
    "delete",
)
_DEFAULT_BACKOFF_TIMES: Final = tuple(
    web_utils._DEFAULT_BACKOFF_FACTOR * (2**i)
    for i in range(web_utils._DEFAULT_MAX_RETRIES)
)


@fixture
def http_func_details(request: PytestRequest) -> str:
    """Simple fixture to extract the param from the request."""
    return str(request.param)


@fixture
def http_method(http_func_details: str) -> str:
    """The HTTP method from the details."""
    return http_func_details.split("-")[-1].upper()


@fixture
def test_url() -> str:
    """Test URL to use."""
    return "http://example.com"


@unit_test
class TestSyncWebUtils:
    """Tests for synchronous web interactions."""

    @fixture
    def http_func(
        self, http_func_details: str, http_method: str
    ) -> Callable[..., Response]:
        """The actual HTTP function to use.

        This will either be the syntactic sugar version (i.e. `.get(...)`) or the direct
        version (i.e. `.request(method="GET", ...)` depending on the form of
        http_func_details.
        """
        if http_func_details.startswith("request"):
            return partial(web_utils.request, method=http_method)
        else:
            return cast(
                Callable[..., Response], getattr(web_utils, http_method.lower())
            )

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    @pytest.mark.parametrize("status_code", _HTTP_STATUS_CODES)
    @responses.activate
    def test_retry_handles_http_status_codes(
        self,
        http_func: Callable[..., Response],
        http_method: str,
        remove_web_retry_backoff_sleep: Optional[Mock],
        status_code: int,
        test_url: str,
    ) -> None:
        """Test that auto retry occurs for expected HTTP status codes.

        Checks for all status codes and HTTP method combinations.
        """
        # Check retry sleep is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            url=test_url,
            status=status_code,
            method=http_method,
        )

        resp = http_func(url=test_url)

        assert resp.status_code == status_code
        assert resp.request.method == http_method

        # Construct expected values depending on if retryable
        if status_code in web_utils._RETRY_STATUS_CODES:
            expected_req_count = 1 + web_utils._DEFAULT_MAX_RETRIES
            expected_sleep_calls = [call(i) for i in _DEFAULT_BACKOFF_TIMES]
        else:
            expected_req_count = 1
            expected_sleep_calls = []

        # Check if retries occurred as expected
        responses.assert_call_count(test_url, expected_req_count)

        # Check sleep called as expected
        assert remove_web_retry_backoff_sleep.call_args_list == expected_sleep_calls

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    @responses.activate
    def test_retry_handles_connection_error(
        self,
        caplog: LogCaptureFixture,
        http_func: Callable[..., Response],
        http_method: str,
        remove_web_retry_backoff_sleep: Optional[Mock],
        test_url: str,
    ) -> None:
        """Test that retry occurs when connection error occurs.

        Tests for all HTTP method types.
        """
        # Check retry sleep is patched
        assert remove_web_retry_backoff_sleep is not None

        # By not adding a URL to `responses` we can force a ConnectionError to be raised
        with pytest.raises(requests.ConnectionError), caplog.at_level(logging.DEBUG):
            http_func(url=test_url)

        # Check sleep called as expected
        assert remove_web_retry_backoff_sleep.call_args_list == [
            call(i) for i in _DEFAULT_BACKOFF_TIMES
        ]

        # Check logs assert this
        debug_logs = get_debug_logs(caplog)
        for retry_count, backoff in [
            (i + 1, backoff) for i, backoff in enumerate(_DEFAULT_BACKOFF_TIMES)
        ]:
            backoff_message_regex = (
                rf"Connection error \(.*\) for {http_method}:{test_url}/?;"
                rf" will retry in {backoff} seconds \(attempt {retry_count}\)\."
            )
            assert re.search(backoff_message_regex, debug_logs, re.DOTALL)

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    @responses.activate
    def test_retry_handles_empty_connection_error(
        self,
        caplog: LogCaptureFixture,
        http_func: Callable[..., Response],
        http_method: str,
        remove_web_retry_backoff_sleep: Optional[Mock],
        test_url: str,
    ) -> None:
        """Test that retry occurs if empty ConnectionError occurs.

        That is one that doesn't contain the request object.

        Rests for all HTTP method types.
        """
        # Check retry sleep is patched
        assert remove_web_retry_backoff_sleep is not None

        # To force an empty ConnectionError, we need to set the exception manually
        # on the response
        exc = requests.ConnectionError("err_str")
        responses.add(
            method=http_method,
            url=test_url,
            body=exc,
        )

        with pytest.raises(
            requests.ConnectionError, match=re.escape("err_str")
        ), caplog.at_level(logging.DEBUG):
            http_func(url=test_url)

        # Check sleep called as expected
        assert remove_web_retry_backoff_sleep.call_args_list == [
            call(i) for i in _DEFAULT_BACKOFF_TIMES
        ]

        # Check logs assert this
        debug_logs = get_debug_logs(caplog)
        for retry_count, backoff in [
            (i + 1, backoff) for i, backoff in enumerate(_DEFAULT_BACKOFF_TIMES)
        ]:
            backoff_message_regex = (
                rf"Connection error \({str(exc)}\);"
                rf" will retry in {backoff} seconds \(attempt {retry_count}\)\."
            )
            assert re.search(backoff_message_regex, debug_logs, re.DOTALL)

    @pytest.mark.parametrize(
        "backoff_factor",
        (None, 2 * web_utils._DEFAULT_BACKOFF_FACTOR),
        ids=["default_backoff", "non_default_backoff"],
    )
    @pytest.mark.parametrize(
        "max_retries",
        (None, 2 * web_utils._DEFAULT_MAX_RETRIES),
        ids=["default_max_retries", "non_default_max_retries"],
    )
    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=(
            "head",
            "get",
            "post",
            "put",
            "patch",
            "delete",
        ),
        indirect=True,
    )
    @responses.activate
    def test_decorator_works_with_diff_args(
        self,
        backoff_factor: Optional[int],
        http_method: str,
        max_retries: Optional[int],
        remove_web_retry_backoff_sleep: Optional[Mock],
        test_url: str,
    ) -> None:
        """Tests that the retry decorator works when used with args or brackets."""
        # Check retry sleep is patched
        assert remove_web_retry_backoff_sleep is not None

        class _DecKwargs(TypedDict):
            # This class is just to assuage mypy when we pass it to the decorator later
            max_retries: NotRequired[int]
            backoff_factor: NotRequired[int]

        dec_kwargs: _DecKwargs = {}
        if max_retries:
            dec_kwargs["max_retries"] = max_retries
        if backoff_factor:
            dec_kwargs["backoff_factor"] = backoff_factor

        # Decorator call will either be empty brackets, "max_retries=X",
        # "backoff_factor=X", or "max_retries=X, backoff_factor=X"
        @_auto_retry_request(**dec_kwargs)
        def request_(*args: Any, **kwargs: Any) -> Response:
            return requests.request(*args, **kwargs)

        with pytest.raises(requests.ConnectionError):
            request_(method=http_method, url=test_url)

        # Check sleep/retry was as expected
        used_backoff_factor = (
            backoff_factor if backoff_factor else web_utils._DEFAULT_BACKOFF_FACTOR
        )
        used_max_retries = (
            max_retries if max_retries else web_utils._DEFAULT_MAX_RETRIES
        )
        expected_backoff_times = tuple(
            used_backoff_factor * (2**i) for i in range(used_max_retries)
        )
        assert remove_web_retry_backoff_sleep.call_args_list == [
            call(i) for i in expected_backoff_times
        ]

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    @pytest.mark.parametrize(
        "provide_timeout", (True, False), ids=lambda x: f"provide_timeout={x}"
    )
    @responses.activate
    def test_default_timeout_set_if_missing(
        self,
        caplog: LogCaptureFixture,
        http_func: Callable[..., Response],
        http_method: str,
        provide_timeout: bool,
        test_url: str,
    ) -> None:
        """Tests that default timeout handling works correctly."""
        if provide_timeout:
            # Ensure a distinct value for the set timeout
            timeout = web_utils._DEFAULT_TIMEOUT / 2
        else:
            timeout = web_utils._DEFAULT_TIMEOUT

        responses.add(
            method=http_method,
            url=test_url,
            match=[
                responses.matchers.request_kwargs_matcher({"timeout": timeout}),
            ],
        )

        with caplog.at_level(logging.DEBUG):
            if provide_timeout:
                http_func(url=test_url, timeout=timeout)
            else:
                http_func(url=test_url)

        # Check logs
        debug_logs = get_debug_logs(caplog)
        expected_log = (
            f"No request timeout provided,"
            f" setting to default timeout ({web_utils._DEFAULT_TIMEOUT}s)"
        )
        if provide_timeout:
            assert expected_log not in debug_logs
        else:
            assert expected_log in debug_logs


@unit_test
class TestASyncWebUtils:
    """Tests for asynchronous web interactions."""

    @fixture
    def http_func(
        self, http_func_details: str, http_method: str
    ) -> Callable[..., Awaitable[httpx.Response]]:
        """The actual HTTP function to use.

        This will either be the syntactic sugar version (i.e. `.async_get(...)`)
        or the direct version (i.e. `.async_request(method="GET", ...)` depending
        on the form of http_func_details.
        """
        if http_func_details.startswith("request"):
            return partial(web_utils.async_request, method=http_method)
        else:
            return cast(
                Callable[..., Awaitable[httpx.Response]],
                getattr(web_utils, f"async_{http_method.lower()}"),
            )

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    @pytest.mark.parametrize("status_code", _HTTP_STATUS_CODES)
    async def test_retry_handles_http_status_codes(
        self,
        http_func: Callable[..., Awaitable[httpx.Response]],
        http_method: str,
        httpx_mock: HTTPXMock,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        status_code: int,
        test_url: str,
    ) -> None:
        """Test that auto retry occurs for expected HTTP status codes.

        Checks for all status codes and HTTP method combinations.
        """
        # Check retry sleep is patched
        assert remove_async_web_retry_backoff_sleep is not None

        httpx_mock.add_response(
            url=test_url,
            status_code=status_code,
            method=http_method,
        )

        resp = await http_func(url=test_url)

        assert resp.status_code == status_code
        assert resp.request.method == http_method

        # Construct expected values depending on if retryable
        if status_code in web_utils._RETRY_STATUS_CODES:
            expected_req_count = 1 + web_utils._DEFAULT_MAX_RETRIES
            expected_sleep_calls = [call(i) for i in _DEFAULT_BACKOFF_TIMES]
        else:
            expected_req_count = 1
            expected_sleep_calls = []

        # Check if retries occurred as expected
        assert len(httpx_mock.get_requests(url=test_url)) == expected_req_count

        # Check sleep called as expected
        assert (
            remove_async_web_retry_backoff_sleep.await_args_list == expected_sleep_calls
        )

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    async def test_retry_handles_connection_error(
        self,
        caplog: LogCaptureFixture,
        http_func: Callable[..., Awaitable[httpx.Response]],
        http_method: str,
        httpx_mock: HTTPXMock,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        test_url: str,
    ) -> None:
        """Test that retry occurs when connection error occurs.

        Tests for all HTTP method types.
        """
        # Check retry sleep is patched
        assert remove_async_web_retry_backoff_sleep is not None

        httpx_mock.add_exception(httpx.ConnectError("err_str"), url=test_url)

        with pytest.raises(httpx.ConnectError), caplog.at_level(logging.DEBUG):
            await http_func(url=test_url)

        # Check sleep called as expected
        assert remove_async_web_retry_backoff_sleep.await_args_list == [
            call(i) for i in _DEFAULT_BACKOFF_TIMES
        ]

        # Check logs assert this
        debug_logs = get_debug_logs(caplog)
        for retry_count, backoff in [
            (i + 1, backoff) for i, backoff in enumerate(_DEFAULT_BACKOFF_TIMES)
        ]:
            backoff_message_regex = (
                rf"Connection error \(.*\) for {http_method}:{test_url}/?;"
                rf" will retry in {backoff} seconds \(attempt {retry_count}\)\."
            )
            assert re.search(backoff_message_regex, debug_logs, re.DOTALL)

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    async def test_retry_handles_empty_connection_error(
        self,
        caplog: LogCaptureFixture,
        http_func: Callable[..., Awaitable[httpx.Response]],
        http_method: str,
        httpx_mock: HTTPXMock,
        mocker: MockerFixture,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        test_url: str,
    ) -> None:
        """Test that retry occurs if empty ConnectionError occurs.

        That is one that doesn't contain the request object.

        Rests for all HTTP method types.
        """
        # Check retry sleep is patched
        assert remove_async_web_retry_backoff_sleep is not None

        # To force an empty ConnectError, we need to set the exception manually
        # on the response. We need to set the request property getter to raise an
        # exceptions as this signifies that the request has not been set.
        def _property_mock_getter_exception(*args: Any) -> None:
            if len(args) != 0:
                # Setter called
                return None
            else:
                # Getter called
                raise RuntimeError

        exc = httpx.ConnectError("err_str")
        mocker.patch.object(
            type(exc),
            "request",
            PropertyMock(side_effect=_property_mock_getter_exception),
        )
        httpx_mock.add_exception(exc, url=test_url)

        with pytest.raises(
            httpx.ConnectError, match=re.escape("err_str")
        ), caplog.at_level(logging.DEBUG):
            await http_func(url=test_url)

        # Check sleep called as expected
        assert remove_async_web_retry_backoff_sleep.await_args_list == [
            call(i) for i in _DEFAULT_BACKOFF_TIMES
        ]

        # Check logs assert this
        debug_logs = get_debug_logs(caplog)
        for retry_count, backoff in [
            (i + 1, backoff) for i, backoff in enumerate(_DEFAULT_BACKOFF_TIMES)
        ]:
            backoff_message_regex = (
                rf"Connection error \({str(exc)}\);"
                rf" will retry in {backoff} seconds \(attempt {retry_count}\)\."
            )
            assert re.search(backoff_message_regex, debug_logs, re.DOTALL)

    @pytest.mark.parametrize(
        "backoff_factor",
        (None, 2 * web_utils._DEFAULT_BACKOFF_FACTOR),
        ids=["default_backoff", "non_default_backoff"],
    )
    @pytest.mark.parametrize(
        "max_retries",
        (None, 2 * web_utils._DEFAULT_MAX_RETRIES),
        ids=["default_max_retries", "non_default_max_retries"],
    )
    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=(
            "head",
            "get",
            "post",
            "put",
            "patch",
            "delete",
        ),
        indirect=True,
    )
    async def test_decorator_works_with_diff_args(
        self,
        backoff_factor: Optional[int],
        http_method: str,
        httpx_mock: HTTPXMock,
        max_retries: Optional[int],
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        test_url: str,
    ) -> None:
        """Tests that the retry decorator works when used with args or brackets."""
        # Check retry sleep is patched
        assert remove_async_web_retry_backoff_sleep is not None

        class _DecKwargs(TypedDict):
            # This class is just to assuage mypy when we pass it to the decorator later
            max_retries: NotRequired[int]
            backoff_factor: NotRequired[int]

        dec_kwargs: _DecKwargs = {}
        if max_retries:
            dec_kwargs["max_retries"] = max_retries
        if backoff_factor:
            dec_kwargs["backoff_factor"] = backoff_factor

        # Decorator call will either be empty brackets, "max_retries=X",
        # "backoff_factor=X", or "max_retries=X, backoff_factor=X"
        @_auto_retry_request(**dec_kwargs)
        async def request_(*args: Any, **kwargs: Any) -> httpx.Response:
            async with httpx.AsyncClient() as client:
                return await client.request(*args, **kwargs)

        httpx_mock.add_exception(httpx.ConnectError("err_str"))

        with pytest.raises(httpx.ConnectError):
            await request_(method=http_method, url=test_url)

        # Check sleep/retry was as expected
        used_backoff_factor = (
            backoff_factor if backoff_factor else web_utils._DEFAULT_BACKOFF_FACTOR
        )
        used_max_retries = (
            max_retries if max_retries else web_utils._DEFAULT_MAX_RETRIES
        )
        expected_backoff_times = tuple(
            used_backoff_factor * (2**i) for i in range(used_max_retries)
        )
        assert remove_async_web_retry_backoff_sleep.await_args_list == [
            call(i) for i in expected_backoff_times
        ]

    @pytest.mark.parametrize(
        argnames="http_func_details",
        argvalues=_HTTP_CALL_TYPES,
        indirect=True,
    )
    @pytest.mark.parametrize(
        "provide_timeout", (True, False), ids=lambda x: f"provide_timeout={x}"
    )
    async def test_default_timeout_set_if_missing(
        self,
        caplog: LogCaptureFixture,
        http_func: Callable[..., Awaitable[httpx.Response]],
        http_method: str,
        httpx_mock: HTTPXMock,
        provide_timeout: bool,
        test_url: str,
    ) -> None:
        """Tests that default timeout handling works correctly."""
        if provide_timeout:
            # Ensure a distinct value for the set timeout
            timeout = web_utils._DEFAULT_TIMEOUT / 2
        else:
            timeout = web_utils._DEFAULT_TIMEOUT

        def check_timeout_callback(request: httpx.Request) -> Optional[httpx.Response]:
            # The form of the HTTPX timeout information is a dict of different timeouts
            assert request.extensions["timeout"] == {
                k: timeout for k in ("connect", "pool", "read", "write")
            }
            return httpx.Response(status_code=200)

        httpx_mock.add_callback(
            callback=check_timeout_callback,
            method=http_method,
            url=test_url,
        )

        with caplog.at_level(logging.DEBUG):
            if provide_timeout:
                await http_func(url=test_url, timeout=timeout)
            else:
                await http_func(url=test_url)

        # Check logs
        debug_logs = get_debug_logs(caplog)
        expected_log = (
            f"No request timeout provided,"
            f" setting to default timeout ({web_utils._DEFAULT_TIMEOUT}s)"
        )
        if provide_timeout:
            assert expected_log not in debug_logs
        else:
            assert expected_log in debug_logs
