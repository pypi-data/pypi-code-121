from unittest.mock import Mock

import pytest
import requests


APPLICATION_JSON = "application/json"


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests.

    Any attempts to create http requests in tests will fail.
    """
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture
def patch_request(monkeypatch):
    def response(mock_response: Mock, method: str = "get") -> Mock:
        mock_request = Mock(return_value=mock_response)
        monkeypatch.setattr(requests, method, mock_request)
        return mock_request

    return response


@pytest.fixture
def patch_request_side_effect(monkeypatch):
    def response(side_effect, method: str = "get") -> Mock:
        mock_request = Mock(side_effect=side_effect)
        monkeypatch.setattr(requests, method, mock_request)
        return mock_request

    return response
