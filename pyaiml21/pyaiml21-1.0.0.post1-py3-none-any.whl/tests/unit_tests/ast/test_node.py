from cgitb import text
import pytest
from pyaiml21.ast import Node


def test_text_constructor():
    node = Node.Value("some text", filename="ai.aiml", line=5)
    assert node.is_text_node
    assert node.text == "some text"
    assert node.filename == "ai.aiml"
    assert node.line == 5

    node = Node.Element("tag", attribs={ "a": Node.Value("5")})
    assert not node.is_text_node
    assert node.tag == "tag"
    assert len(node.attributes) == 1
    assert "a" in node.attributes
    assert len(node.children) == 0

    with pytest.raises(ValueError):
        node = Node(tag="some tag", text="some text")

    with pytest.raises(ValueError):
        node = Node()


def test_empty_str():
    b = Node.Element("b")
    assert str(b) == "<b></b>"


def test_str():
    text_node = Node.Value("abc")
    a = Node.Element("a")
    b = Node.Element("b")
    c = Node.Element("c")
    a.children = [b, c]
    b.parent = a
    c.parent = a
    b.children = [text_node]
    text_node.parent = b

    assert str(text_node) == "abc"
    assert str(b) == "<b>abc</b>"
    assert str(a) == "<a><b>abc</b><c></c></a>"
