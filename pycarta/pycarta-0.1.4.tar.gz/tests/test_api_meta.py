import json
import pytest

from pycarta.api.meta import (
    get_meta,
    get_actors,
    get_selectors,
    get_schema
)

from .common_fixtures import agent, cartaAuth, cartaUrl


def test_meta(agent):
    response = get_meta(agent, verify=False)
    assert response is not None


def test_actors(agent):
    response = get_actors(agent, verify=False)
    assert response is not None


def test_selectors(agent):
    response = get_selectors(agent, verify=False)
    assert response is not None

def test_schema(agent):
    # no actor or selector exists with that name
    response = get_schema(agent, "foo", verify=False)
    assert response is None
    # actor
    response = get_schema(agent, "aggregate", verify=False)
    assert response is not None
    # selector
    response = get_schema(agent, "vertexName", verify=False)
    assert response is not None
