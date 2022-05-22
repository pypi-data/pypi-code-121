from itertools import chain
from . import Node, Collection, Empty


def element_clone(el):
    new = Element(el.tag, attrib=el.attrib)
    new.text = el.text
    new.extend(clone(child) for child in el)
    return new


def clone(el):
    # copy.deepcopy doesn't copy type
    if isinstance(el, Node):
        return Node(el.tag, el.text, attrib=el.attrib)
    elif isinstance(el, Collection):
        children = (clone(child) for child in el)
        return Collection(el.tag, children, attrib=el.attrib)
    elif isinstance(el, Empty):
        return Empty(el.tag, attrib=el.attrib)
    else:
        raise TypeError


def traverse(el):
    # you can also do yield from el.iter(), but this is more fun
    yield el
    yield from chain.from_iterable(map(traverse, el))
