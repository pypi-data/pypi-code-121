import json
import pytest

from pycarta.api.workflow import (
    get_workflows,
    get_operations
)

from .common_fixtures import agent, cartaAuth, cartaUrl


def test_workflows(agent):
    response = get_workflows(agent, verify=False)
    assert response is not None


def test_operations(agent):
    # get workflows
    workflows = get_workflows(agent, verify=False)
    # get operations from a workflow that does not exist
    response = get_operations(agent, name="foobar", verify=False)
    assert response is None
    response = get_operations(agent, id="1234567890987654321", verify=False)
    assert response is None
    # test a workflow that exists
    try:
        name = workflows[0]["name"]
    except IndexError:
        response = get_operations(agent, name=None, verify=False)
        assert response is None
    else:
        pass
