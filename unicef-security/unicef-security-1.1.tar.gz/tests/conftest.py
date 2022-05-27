import pytest

from tests.demoproject.factories import UserFactory


@pytest.fixture()
def auth_user():
    return UserFactory()
