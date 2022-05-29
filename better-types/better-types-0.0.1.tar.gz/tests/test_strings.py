import pytest

from better import strings


def test_shuffle():
    source = "abcdef"
    result = strings.shuffle(source)

    assert result != source
    assert len(result) == len(source)
    assert sorted(result) == sorted(source)


@pytest.mark.parametrize(
    "string, expected",
    [
        ('""', True),
        ('"a string"', True),
        ('{"key":"value"}', True),
        ("a string without quotes", False),
        ("", False),
        (":", False),
    ],
)
def test_is_json(string: str, expected: bool):
    assert strings.is_json(string) is expected
