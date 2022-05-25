import os

import pytest

from tktl.core.clients import DeploymentApiClient
from tktl.core.clients.future.taktile import (
    DeploymentApiClient as FutureDeploymentApiClient,
)
from tktl.core.config import set_api_key
from tktl.core.exceptions import TaktileSdkError


def test_instantiate_taktile_client():
    key = os.environ["TEST_USER_API_KEY"]
    set_api_key(key)
    client = DeploymentApiClient()
    with pytest.raises(TaktileSdkError):
        client.get_endpoint_by_name("admin/df.asfm", "", "")
    assert "X-Api-Key" in client._headers
    assert client._headers["X-Api-Key"] == key


def test_instantiate_taktile_client_future():
    key = os.environ["TEST_USER_API_KEY"]
    set_api_key(key)
    client = FutureDeploymentApiClient(api_key=key)
    with pytest.raises(TaktileSdkError):
        client.get_endpoint_by_name("admin/df.asfm", "", "")
    assert "X-Api-Key" in client._headers
    assert client._headers["X-Api-Key"] == key
