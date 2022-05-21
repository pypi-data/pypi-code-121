from typing import Tuple, Optional
from pyaiml21.ast import Node


__all__ = ["unqname", "is_aiml_str", "handle_text_child"]


def unqname(tag: str) -> Tuple[str, Optional[str]]:
    """Disassemble qualified name into tag name and namespace."""
    maybe_ns, _, name = tag.rpartition("}")
    if maybe_ns.startswith("{"):
        ns = maybe_ns[1:]
        return name, ns
    return name, None


def is_aiml_str(s: str) -> bool:
    """
    Check is `s` is valid AIML tag/attribute name.

    Since the only version that defines a namespace for aiml
    elements is 1.0.1 with the corresponding namespace url
        http://alicebot.org/2001/AIML-1.0.1
    here we check that the element either doesnot have any
    namespace assigned or the namespace is the one above.

    Note that lxml will resolve namespace names to urls for us.
    """
    AIML1_0_1_ns = "http://alicebot.org/2001/AIML-1.0.1"
    _, ns = unqname(s)
    return ns is None or ns == AIML1_0_1_ns


def _strip_text(text: str) -> str:
    """
    Remove whitespaces from the beginning and end.

    If any were present, keep one space on the corresponding side.
    """
    ltext = text.lstrip()
    rtext = ltext.rstrip()
    if not rtext:
        return ""
    if len(ltext) < len(text):
        rtext = " " + rtext
    if len(rtext) < len(ltext):
        rtext += " "
    return text


def handle_text_child(child: str, parent: Node) -> None:
    """
    Convert `child` string to ast.Node, appending it to parents children.

    Before the string is stripped off of whitespaces and
    non-empty string is added to the ast.
    """
    # remove empty spaces, if the string contains only spaces, keep just one
    # space
    if not child:
        return
    stripped = _strip_text(child)
    if not stripped:
        stripped = " "
    node = Node.Value(stripped, parent, parent.filename, parent.line,
                      parent.col, parent.aiml_version)
    parent.children.append(node)
