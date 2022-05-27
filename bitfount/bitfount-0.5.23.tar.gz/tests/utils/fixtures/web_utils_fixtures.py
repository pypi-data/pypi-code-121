"""Fixtures for the web_utils module."""
import asyncio
import time
from typing import Optional
from unittest.mock import AsyncMock, Mock

from pytest import fixture
from pytest_mock import MockerFixture

from tests.utils import PytestRequest
from tests.utils.helper import end_to_end_mocks_test, integration_test, unit_test


@fixture(autouse=True)
def remove_web_retry_backoff_sleep(
    mocker: MockerFixture, request: PytestRequest
) -> Optional[Mock]:
    """Removes backoff sleep for the auto_retry functionality.

    As we don't want to slow down tests unnecessarily, this fixture mocks out
    the sleep that would normally occur in the automatic retry of web interactions.
    """
    # Only mock it out for tests that don't actually perform web interactions
    # i.e. not e2e or tutorial tests
    if any(
        mark.name in request.keywords
        for mark in (unit_test, integration_test, end_to_end_mocks_test)
    ):
        # Need to patch entire imported module but only want to mock out `.sleep`
        # calls so set that explicitly to a Mock that isn't wrapping
        mock_time: Mock = mocker.patch("bitfount.web_utils.time", wraps=time)
        mock_time.sleep = Mock()
        return mock_time.sleep
    else:
        return None


@fixture(autouse=True)
def remove_async_web_retry_backoff_sleep(
    mocker: MockerFixture, request: PytestRequest
) -> Optional[AsyncMock]:
    """Removes backoff sleep for the async auto_retry functionality.

    As we don't want to slow down tests unnecessarily, this fixture mocks out
    the sleep that would normally occur in the automatic retry of web interactions.
    """
    # Only mock it out for tests that don't actually perform web interactions
    # i.e. not e2e or tutorial tests
    if any(
        mark.name in request.keywords
        for mark in (unit_test, integration_test, end_to_end_mocks_test)
    ):
        # Need to patch entire imported module but only want to mock out `.sleep`
        # calls so set that explicitly to a Mock that isn't wrapping
        mock_async: Mock = mocker.patch("bitfount.web_utils.asyncio", wraps=asyncio)
        mock_async.sleep = AsyncMock()
        return mock_async.sleep
    else:
        return None
