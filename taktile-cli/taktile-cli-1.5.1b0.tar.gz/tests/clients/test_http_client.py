import os

import pytest
import requests
from pydantic import BaseModel

from tktl.core.clients import API
from tktl.core.config import set_api_key, settings


def test_instantiate_api_client():
    key = os.environ["TEST_USER_API_KEY"]
    set_api_key(key)
    client = API(api_base=settings.DEPLOYMENT_API_URL, api_key=key)
    assert "X-Api-Key" in client._headers
    assert client._headers["X-Api-Key"] == key
    assert client._base == f"{settings.DEPLOYMENT_API_URL}"


@pytest.mark.parametrize("verb", [("post"), ("get"), ("patch"), ("put"), ("delete")])
def test_request_failures(verb: str):
    client = API(api_base=settings.DEPLOYMENT_API_URL)
    with pytest.raises(requests.exceptions.RequestException):
        client.call(verb=verb, path="non/existent/path")


def test_interpret_response():
    client = API(api_base=settings.DEPLOYMENT_API_URL)

    with pytest.raises(requests.exceptions.HTTPError):
        client.call(verb="post", path="non/existent/path", model=BaseModel)

    class TestModel(BaseModel):
        id: int
        title: str

    client = API(api_base="https://my-json-server.typicode.com/typicode/demo/posts/1")
    response = client.call(verb="get", path="", model=TestModel)

    assert response.dict()["id"] == 1
