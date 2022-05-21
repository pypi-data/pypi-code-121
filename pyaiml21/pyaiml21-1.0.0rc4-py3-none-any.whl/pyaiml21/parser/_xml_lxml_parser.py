"""
XML parser based on `lxml` library.

This module contains a definition of XML parser that parses
XML and returns the intermediate representation (ast/) of the
document.
"""
from lxml import etree
from typing import Optional, Union
from pathlib import Path
from pyaiml21.aiml import AIMLVersion, DEFAULT_VERSION
from pyaiml21.ast import Node
from .logger import Logger
from ._xml_utils import unqname, is_aiml_str, handle_text_child


# for type checking
XmlNode = etree._Element


def _get_line(node: XmlNode) -> int:
    assert hasattr(node, "sourceline")
    line: int = getattr(node, "sourceline")
    return line


def _make_parser():
    """Return the parser we use to parse XML files."""
    return etree.XMLParser(
        # remove_blank_text=True,  # ignore empty text
        remove_comments=True,  # ignore all comments
        resolve_entities=False  # prevent xml entity resolution attacks
    )


def _xml_text(txt: Union[bytes, str]) -> str:
    """
    Convert lxml returned text to `str`.

    lxml might actually return bytes, so we convert it back
    to the string.
    """
    if isinstance(txt, bytes):
        return bytes.decode(txt, encoding="utf-8")
    return txt


def _non_aiml_node(node: XmlNode,
                   parent: Node,
                   filename: Optional[str],
                   version: Optional[AIMLVersion]) -> None:
    """
    Transform non-aiml node.

    For non-aiml nodes, we transform them back to the strings
    and recursively call `_transform_xml_tree` for children.
    """
    texts = [f"<{node.tag}"]
    for name, attr in node.attrib.items():
        texts.append(f"{_xml_text(name)}=\"{_xml_text(attr)}\"")
    texts.append(f">{node.text}")
    handle_text_child(" ".join(texts), parent)
    for child in node:
        _transform_xml_tree(child, parent, filename, version)
    handle_text_child(f"</{node.tag}>{node.tail}", parent)


def _transform_xml_tree(root: XmlNode,
                        parent: Optional[Node],
                        filename: Optional[str],
                        version: Optional[AIMLVersion]) -> Node:
    """Transform lxml.AST to Node.AST."""
    # first we prepare root' node
    lineno = _get_line(root)
    name, _ = unqname(root.tag)
    node = Node.Element(name, parent, {}, [], filename, lineno, None, version)

    # then each attribute convert to the corresponding ast.Node
    for key, val in root.attrib.items():
        name, attr = map(_xml_text, [key, val])
        v = Node.Value(attr, node, filename, node.line, version=version)
        if is_aiml_str(name):
            attr_name, _ = unqname(name)
            node.attributes[attr_name] = v
        else:
            node.attributes[name] = v

    # check text element
    if root.text:
        handle_text_child(root.text, node)

    # transform children
    for el in root:
        if not is_aiml_str(el.tag):
            _non_aiml_node(el, node, filename, version)
            continue
        _transform_xml_tree(el, node, filename, version)
        if el.tail:
            handle_text_child(el.tail, node)

    # lastly we need to append `node` to parent's children, for
    # _non_aiml_node to work properly
    if parent:
        parent.children.append(node)

    assert isinstance(node, Node)
    return node


class LXMLParser:
    """
    lxml parser used to parse raw XML within the interpreter and chatbots.

    A collection of functions to parse raw XML and convert it to the AST
    representation defined in `pyaiml21.ast.node`.
    """

    @staticmethod
    def _parse_version(root: XmlNode, logger: Logger, file: str) \
            -> AIMLVersion:
        """Parse and return the version attribute of <aiml> tag."""
        tag, _ = unqname(root.tag)

        # if the root element is not <aiml> element, we fail here
        if tag != "aiml":
            logger.error_xml_syntax(
                "Root element must be the <aiml> tag",
                file, _get_line(root), None
            )
            return DEFAULT_VERSION

        # if not version is specified we use the default version that should
        # enable the latest language features, note that this might cause
        # false-alarm deprecation warnings
        if "version" not in root.attrib:
            return DEFAULT_VERSION

        declared_version = _xml_text(root.attrib["version"])
        if declared_version not in AIMLVersion:
            assert isinstance(root.sourceline, int) or root.sourceline is None
            logger.warn_xml_syntax(
                f"Unexpected version value: {declared_version}, "
                f"defaulting to: {DEFAULT_VERSION.value}",
                file, root.sourceline
            )
            return DEFAULT_VERSION
        return AIMLVersion(declared_version)

    @staticmethod
    def _parse(source: str, logger: Logger, is_file: bool) -> Optional[Node]:
        filename = str(Path(source).absolute()) if is_file else "(from text)"
        parser = _make_parser()
        try:
            if is_file:
                r = etree.parse(source, parser).getroot()
            else:
                r = etree.fromstring(source, parser)
            assert isinstance(r, XmlNode)
            version = LXMLParser._parse_version(r, logger, filename)
            return _transform_xml_tree(r, None, filename, version)
        except etree.XMLSyntaxError as e:
            msg = e.msg or "unknown xml syntax error"
            logger.error_xml_syntax(msg, filename, *e.position)
            return None

    @staticmethod
    def parse(filename: str, logger: Logger) -> Optional[Node]:
        """Parse and transform XML-AIML file to the `Node`-AST."""
        if not filename.endswith(".aiml"):
            raise ValueError(f"Expected .aiml file, got {filename}")
        return LXMLParser._parse(filename, logger, True)

    @staticmethod
    def parse_text(text: str, logger: Logger) -> Optional[Node]:
        """Parse and transform XML text to the `Node`-AST."""
        return LXMLParser._parse(text, logger, False)
