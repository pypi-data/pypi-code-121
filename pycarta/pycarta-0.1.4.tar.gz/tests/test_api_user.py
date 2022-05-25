import json
import pytest

from pycarta.api.user import get_user, get_users
from pycarta.api.user import is_authenticated

from .common_fixtures import agent, cartaAuth, cartaUrl


@pytest.fixture
def expected_user():
    with open("expected_output.json", "rb") as ifs:
        return json.load(ifs)["api"]["user"]

@pytest.fixture
def filtered_users():
    with open("expected_output.json", "rb") as ifs:
        return json.load(ifs)["api"]["filtered users"]


def test_user(agent, expected_user):
    # get the user, but localhost certificate is not recognized,
    # so pass verify=False.
    actual = get_user(agent, verify=False)
    assert actual == expected_user


def test_authenticated(agent):
    auth = is_authenticated(agent, verify=False)
    assert auth, "User is not authenticated."


def test_users(agent, filtered_users):
    # successful
    response = get_users(
        agent,
        attribute="UserName",
        value="m",
        filter="startswith",
        verify=False
    )
    assert response == filtered_users
    # Expected failure conditions
    # Invalid attribute
    try:
        invalid = get_users(
            agent,
            attribute="FooBar",
            value="m",
            filter="startswith",
            verify=False
        )
    except ValueError as err:
        pass
    else:
        assert False, \
            "Attribute =!= UserName, Email, FirstName, LastName " \
            "should raise a ValueError."
    # Invalid comparison method
    try:
        invalid = get_users(
            agent,
            attribute="UserName",
            value="m",
            filter="foobar",
            verify=False
        )
    except ValueError as err:
        pass
    else:
        assert False, \
            "Method =!= equal, startswith should raise a ValueError."
