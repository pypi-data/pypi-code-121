import pytermgui as ptg
from pytermgui.config import expand_key


def test_expand_key_noexpand():
    assert expand_key(ptg.Splitter, "chars") == (ptg.Splitter, "chars")


def test_expand_key_long():
    assert expand_key(ptg.Splitter, "chars.separator") == (
        ptg.Splitter.chars,
        "separator",
    )
