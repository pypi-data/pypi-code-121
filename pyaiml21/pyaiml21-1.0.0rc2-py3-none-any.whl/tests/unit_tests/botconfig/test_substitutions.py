import pytest
from pyaiml21.botconfig import Substitutions


def test_empty():
    s = Substitutions()
    for text in ("a", "abc", "15sc sfd78", ""):
        assert s.sub(text) == text


def test_get_set_simple():
    s = Substitutions()
    with pytest.raises(Exception):
        _ = s["abc"]

    s["abc"] = "23"
    assert s["abc"] == "23"


def test_complex():
    s = Substitutions()
    text = "little red fox jumped over the cat"

    assert s.sub(text) == text
    s["fox"] = "dog"
    assert s.sub(text) == "little red dog jumped over the cat"
    s["elephant"] = "nothing"
    assert s.sub(text) == "little red dog jumped over the cat"

    s["fox"] = "fox"
    assert s.sub(text) == text

    # capital and small
    s["CAT"] = "mouse"
    assert s.sub(text) ==  "little red fox jumped over the mouse"

    s["LiTTle"] = "ClevER"
    assert s.sub(text) ==  "ClevER red fox jumped over the mouse"
