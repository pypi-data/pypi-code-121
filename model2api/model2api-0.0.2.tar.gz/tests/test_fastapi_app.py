from fastapi.testclient import TestClient
from model2api.api import create_api
from pydantic import BaseModel
from model2api.core import Predictor

import pytest


class X(BaseModel):
    data: str


def dummy(input: X) -> X:
    return input


app = create_api(Predictor(dummy))

client = TestClient(app)


def test_health_actuators():
    response = client.get("/actuators/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up"}


def test_model_endpoint():
    response = client.post("/predict", data='{"data": "test"}')
    assert response.status_code == 200
    assert response.json() == {"data": "test"}


def test_model_endpoint_with_dict():
    response = client.post("/predict", json={"data": "test"})
    assert response.status_code == 200
    assert response.json() == {"data": "test"}


def test_model_doc():
    assert client.get("/").content == client.get("/docs").content
