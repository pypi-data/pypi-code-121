"""Inner node of the AST."""
from typing import Callable, Dict, Optional, List
from pyaiml21.aiml import AIMLVersion


class Node:
    """
    Represents a node in the AST.

    Nodes of the parse tree created from parsed xml files are reconstructed
    using this class to provide uniform access to attributes and children.

    Given the nature of the AIML, especially the fact that attributes
    are allowed to be specified as children, this node represents both
    the attributes and the children as a list of other `Node`'s, and it
    is responsibility of syntax check to make sure, which children are
    attributes.

    To create instances of `Node`, please use static methods `Node.Element`
    and `Node.Value`.
    """

    __slots__ = [
        "tag", "attributes", "children", "text",
        "parent",
        "filename", "line", "col",
        "aiml_version"
    ]

    def __init__(
            self,
            *,
            tag: Optional[str] = None,
            attributes: Optional[Dict[str, "Node"]] = None,
            children: Optional[List["Node"]] = None,
            text: Optional[str] = None,
            parent: Optional["Node"] = None,
            filename: Optional[str] = None,
            line: Optional[int] = None,
            col: Optional[int] = None,
            version: Optional[AIMLVersion] = None
    ):
        """
        Create a node.

        This method should not be called explicitly, use
        `Node.Element` or `Node.Value` to create the appropriate node.

        Exactly one must be defined, either 'text', or 'tag' with any other
        argument except 'text'.

        :param tag: either a string, denoting the tag of the node, or None in
                    case of a text node
        :param attributes: mapping from text to nodes
        :param children: sequence of child nodes
        :param text: in case of all previous being None, this node represents
                     a text node and its text is here
        :param parent: reference to the parent node or None for root node
        :param filename: file, in which the element is defined
        :param line: line of the node's occurrence, or `None`
                              if it is not known
        :param col: column of the node's occurrence, or `None`
                              if it is not known
        """
        if text is None and tag is None:
            raise ValueError(
                "tag or text of the node must be specified, both were None"
            )
        if text is not None and any(
                param is not None for param in (tag, attributes, children)):
            raise ValueError(
                "cannot specify both text and tag-related attributes."
            )

        self.tag = tag
        """tag of the node, or `None` for text node"""
        self.attributes = {} if attributes is None else attributes
        """node's attributes, for text node empty dictionary"""
        self.children: List[Node] = [] \
            if children is None or tag is None \
            else children
        """node's children, text node has no children"""
        self.text = text
        """text content of the node; for non-text nodes `None`"""
        self.parent = parent
        """reference to the parent node in the AST"""
        self.filename = filename
        """file, in which the element is defined"""
        self.line = line
        """line of the element's occurrence if known, else `None`"""
        self.col = col
        """column of the element's occurrence if known, else `None`"""
        self.aiml_version = version
        """the AIML version declared with the <aiml> root element"""

    @property
    def is_text_node(self) -> bool:
        """Return `True` if this node is a text node (without a tag)."""
        return self.text is not None

    def to_xml(self, f: Callable[['Node'], str]) -> str:
        """
        Convert this node to xml representation, applying `f` to all subnodes.

        Return xml representation of this node where `node.tag` is the root
        element and text attributes (nodes with `node.is_text_node == True`)
        are transformed to root's XML attributes.

        If current node is text, return just text.

        Examples:
            >>> discard = lambda x: ""
            >>> text_node = Node.Value("some text")
            >>> text_node.to_xml(discard) == "some text"
            True

            >>> attr = Node.Value("value")
            >>> a = Node.Element("a")
            >>> b = Node.Element("b", attribs={"attr": attr}, children=[a])
            >>> a.parent = b
            >>> attr.parent = b
            >>> b.to_xml(str)
            '<b attr="value"><a></a></b>'
        """
        if self.is_text_node:
            assert isinstance(self.text, str)
            return self.text

        opening_tag = [f"<{self.tag}"]
        children = []

        # check which attributes can be xml attributes or must be children
        for name, node in self.attributes.items():
            if node.is_text_node:
                opening_tag.append(f"{name}=\"{node.text}\"")
            else:
                children.append(f(node))

        # add real children
        children.extend(map(f, self.children))

        return f"{' '.join(opening_tag)}>{''.join(children)}</{self.tag}>"

    def __str__(self):
        """Convert the whole subtree rooted at this node to string."""
        return self.to_xml(str)

    @classmethod
    def Element(
        cls,
        name: str,
        parent: Optional['Node'] = None,
        attribs: Optional[Dict[str, 'Node']] = None,
        children: Optional[List['Node']] = None,
        filename: Optional[str] = None,
        line: Optional[int] = None,
        col: Optional[int] = None,
        version: Optional[AIMLVersion] = None
    ):
        """
        Create an XML <tag> element.

        This class method allows creation of arbitrary nodes in the AST
        representing XML tags. For parameters, see `Node`.

        Example:
            >>> root = Node.Element("root")
            >>> a = Node.Element("a", parent=root)
            >>> root.children.append(a)
            >>> [child.tag for child in root.children] == ["a"]
            True

            >>> root.attributes["name"] = Node.Value("my_node")
            >>> root.is_text_node
            False
            >>> root.text is None
            True
        """
        return cls(
            tag=name, parent=parent, attributes=attribs, children=children,
            filename=filename, line=line, col=col, version=version
        )

    @classmethod
    def Value(
        cls,
        text: str,
        parent: Optional['Node'] = None,
        filename: Optional[str] = None,
        line: Optional[int] = None,
        col: Optional[int] = None,
        version: Optional[AIMLVersion] = None
    ):
        """
        Create a text node in the AST.

        Use this classmethod to construct a text node into the AST.

        Example:
            >>> node = Node.Value("some text")
            >>> node.is_text_node
            True
            >>> node.text == "some text"
            True
            >>> node.tag is None
            True
        """
        return cls(
            parent=parent, text=text,
            filename=filename, line=line, col=col, version=version
        )
