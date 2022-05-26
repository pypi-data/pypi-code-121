import pytest

from puglang.lang.token import Token


@pytest.fixture
def token():
    return Token()


def test_token_is_not_none(token):
    assert token is not None
