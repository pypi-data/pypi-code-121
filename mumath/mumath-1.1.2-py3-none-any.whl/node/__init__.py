import xml.etree.ElementTree as ET
from functools import partial
from types import SimpleNamespace as Namespace
from .mathml import node, collection, empty


class Element(ET.Element):
    def __repr__(self):
        return f"<{self._name()} />"

    def _name(self):
        name = [self.tag]
        for key, value in self.attrib.items():
            name.append(f'{key}="{value}"')
        return " ".join(name)


class Node(Element):
    def __init__(self, tag, text=None, attrib={}, **extra):
        super().__init__(tag, attrib, **extra)
        self.text = text

    def __repr__(self):
        return f"<{self._name()}>{self.text}</{self.tag}>"



class Collection(Element):
    def __init__(self, tag, children=(), attrib={}, **extra):
        super().__init__(tag, attrib, **extra)
        self.extend(children)

    def __repr__(self):
        return f"<{self._name()} with {len(self)} children>"


class Empty(Element):
    # For elements like <mprescripts>, <none>, <mspace>
    pass


class Comment(Element):
    def __repr__(self):
        return f"<!-- {self.text} -->"

_nodes = [
    (Node, node),
    (Collection, collection),
    (Empty, empty),
]


mml = Namespace(**{
    tag: partial(mtype, tag)
    for mtype, tags in _nodes
    for tag in tags
})

html = Namespace(Comment=Comment)

special = Namespace(NO_NUMBER=Empty("NO_NUMBER"))

