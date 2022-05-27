import pytest

from act.types.types import object_validates

PLACEHOLDER = (
    "[placeholder[d12da485a7ae4437499b0d5a97f71c5d33e1a90588717b020f9b1f4c18368be0]]"
)


def test_validator_non_string():
    with pytest.raises(TypeError):
        object_validates("tool", 1)

    with pytest.raises(TypeError):
        object_validates("tool", None)


def test_tool_validator():
    assert object_validates("tool", "Mimikatz") is False
    assert object_validates("tool", "mimikatz") is True
    assert object_validates("tool", "many 0days: ie") is True


def test_threatactor_validator():
    assert object_validates("threatActor", "APT28") is False
    assert object_validates("threatActor", "apT28") is False
    assert object_validates("threatActor", "apt28") is True
    assert object_validates("threatActor", "some-ta") is True
    assert object_validates("threatActor", "some-ta@!") is True
    assert object_validates("threatActor", PLACEHOLDER) is True


def test_uri_validator():
    # Illegal URIs
    assert object_validates("uri", "abc") is False

    # Legal URIs
    assert object_validates("uri", "http://www.mnemonic.no") is True
    assert object_validates("uri", "https://www.mnemonic.no") is True
    assert object_validates("uri", "https://www.mnemonic.no/abc?a=2") is True
    assert object_validates("uri", "https://www.mnemonic.no/a-b-c?a=2") is True
    assert object_validates("uri", "ftp://127.0.0.1") is True

    assert object_validates("uri", PLACEHOLDER) is True
