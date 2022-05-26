import pytest

from puglang.lang.parser import Parser


@pytest.fixture
def parser():
    return Parser()


def test_parser_is_not_none(parser):
    assert parser is not None
