"""Module containing the logic for XML instance as dot object"""

from xml.etree import ElementTree

from dgspoc.utils import DotObject


class DotElement(ElementTree.Element):

    def __init__(self, tag, attrib=None, **extra):
        attrib = attrib or {}

        if 'raw_element' in extra:
            self.raw_element = extra.pop('raw_element')
            extra.update(dict(text=self.raw_element.text,   # noqa
                              tail=self.raw_element.tail))  # noqa
        else:
            self.raw_element = None

        super().__init__(tag, attrib=attrib, **extra)
        self.parent = None

    def __getattribute__(self, item):
        result = super().__getattribute__(item)
        if item == 'attrib':
            if isinstance(result, dict):
                dot_object = DotObject(result)
                return dot_object
            return result
        else:
            return result

    def __repr__(self):
        return "<DotElement %r at %#x>" % (self.tag, id(self))

    def __len__(self):
        return len(self.raw_element) if self.raw_element else len(self)

    def __copy__(self):
        element = super().__copy__()        # noqa
        element.raw_element = self.raw_element
        return element

    def __bool__(self):
        return len(self) != 0

    def __getitem__(self, index):
        if self.raw_element:
            child = self.raw_element[index]
            new_child = to_dot_element(child)
            return new_child
        else:
            child = super().__getitem__(index)
            return child

    def __setitem__(self, index, element):
        if self.raw_element:
            self.raw_element.__setitem__(index, element)
        else:
            super().__setitem__(index, element)

    def __delitem__(self, index):
        if self.raw_element:
            self.raw_element.__delitem__(index)
        else:
            super().__delitem__(index)

    @property
    def has_children(self):
        return len(self.raw_element) if self.raw_element else len(self)

    @property
    def children(self):
        if not self.has_children:
            yield from ()
        cls = self.__class__
        node = self.raw_element if self.raw_element else self
        for child in node:
            if isinstance(child, cls):
                child.parent = self
                yield child
            else:
                kwargs = dict(attrib=child.attrib, raw_element=child)
                new_child = cls(child.tag, **kwargs)
                new_child.parent = self
                yield new_child

    @property
    def raw_children(self):
        if not self.raw_element:
            yield from ()

        for child in self.raw_element:
            yield child

    @property
    def is_leaf(self):
        return not self.has_children

    @property
    def prev_sibling(self):
        try:
            parent = self.parent
            if self.raw_element:
                raw_children = parent.raw_children
                lst = list(raw_children)
                index = lst.index(self.raw_element)
                _prev_sibling = lst[index - 1]
            else:
                lst = list(parent)
                index = lst.index(self)
                _prev_sibling = lst[index - 1]

            return _prev_sibling
        except Exception as ex:     # noqa
            return None

    @property
    def next_sibling(self):
        try:
            parent = self.parent
            if self.raw_element:
                raw_children = parent.raw_children
                lst = list(raw_children)
                index = lst.index(self.raw_element)
                _next_sibling = lst[index + 1]
            else:
                lst = list(parent)
                index = lst.index(self)
                _next_sibling = lst[index + 1]
            return _next_sibling
        except Exception as ex:     # noqa
            return None

    def append(self, subelement):
        if self.raw_element:
            self.raw_element.append(subelement)
        else:
            super().append(subelement)

    def extend(self, elements):
        if self.raw_element:
            self.raw_element.extend(elements)
        else:
            super().extend(elements)

    def insert(self, index, subelement):
        if self.raw_element:
            self.raw_element.insert(index, subelement)
        else:
            super().insert(index, subelement)

    def remove(self, subelement):
        if self.raw_element:
            self.raw_element.remove(subelement)
        else:
            super().remove(subelement)

    def find(self, path, namespaces=None):
        kwargs = dict(namespaces=namespaces)
        if self.raw_element:
            result = self.raw_element.find(path, **kwargs)
        else:
            result = super().find(path, **kwargs)

        for index, item in enumerate(result):
            new_item = to_dot_element(item)
            if new_item != item:
                result[index] = new_item
        return result

    def findtext(self, path, default=None, namespaces=None):
        kwargs = dict(default=default, namespaces=namespaces)
        if self.raw_element:
            result = self.raw_element.findtext(path, **kwargs)
        else:
            result = super().findtext(path, **kwargs)
        return result

    def findall(self, path, namespaces=None):
        kwargs = dict(namespaces=namespaces)
        if self.raw_element:
            result = self.raw_element.findall(path, **kwargs)
        else:
            result = super().findall(path, **kwargs)

        for index, item in enumerate(result):
            new_item = to_dot_element(item)
            if new_item != item:
                result[index] = new_item
        return result

    def iterfind(self, path, namespace=None):
        kwargs = dict(namespace=namespace)
        is_iter = False

        if self.raw_element:
            result = self.raw_element(path, **kwargs)
        else:
            result = super().iterfind(path, **kwargs)

        for node in result:
            is_iter = True
            new_node = to_dot_element(node)
            yield new_node

        if not is_iter:
            yield from ()

    def iter(self, tag=None):
        kwargs = dict(tag=tag)
        is_iter = False

        if self.raw_element:
            result = self.raw_element.iter(**kwargs)
        else:
            result = super().iter(**kwargs)

        for node in result:
            is_iter = True
            new_node = to_dot_element(node)
            yield new_node

        if not is_iter:
            yield from ()

    def clear(self):
        if self.raw_element:
            self.raw_element.clear()
        super().clear()


class DotElementTree(ElementTree.ElementTree):

    def __init__(self, element=None, file=None):
        new_element = to_dot_element(element)
        super().__init__(element=new_element, file=file)

    def getroot(self):
        root = super().getroot()
        kwargs = dict(attrib=root.attrib, raw_element=root)
        new_root = DotElement(root.tag, **kwargs)
        return new_root

    def parse(self, source, parser=None):
        super().parse(source, parser=parser)
        root = self.getroot()
        return root


iselement = ElementTree.iselement


SubElement = ElementTree.SubElement


Comment = ElementTree.Comment


ProcessingInstruction = ElementTree.ProcessingInstruction


PI = ElementTree.PI


register_namespace = ElementTree.register_namespace


def tostring(element, encoding=None, method=None, *,
             xml_declaration=None, default_namespace=None,
             short_empty_elements=True):
    _element = getattr(element, 'raw_element', element)
    kwargs = dict(
        encoding=encoding, method=method,
        xml_declaration=xml_declaration,
        default_namespace=default_namespace,
        short_empty_elements=short_empty_elements
    )
    result = ElementTree.tostring(_element, **kwargs)
    return result


def tostringlist(element, encoding=None, method=None, *,
                 xml_declaration=None, default_namespace=None,
                 short_empty_elements=True):
    _element = getattr(element, 'raw_element', element)
    kwargs = dict(
        encoding=encoding, method=method,
        xml_declaration=xml_declaration,
        default_namespace=default_namespace,
        short_empty_elements=short_empty_elements
    )
    result = ElementTree.tostringlist(_element, **kwargs)
    return result


def dump(elem):
    element = getattr(elem, 'raw_element', elem)
    ElementTree.dump(element)


def parse(source, parser=None):
    tree = DotElementTree()
    tree.parse(source, parser)
    return tree


def to_dot_element(node):
    if isinstance(node, ElementTree.Element):
        kwargs = dict(attrib=node.attrib, raw_element=node)
        new_node = DotElement(node.tag, **kwargs)
        return new_node
    return node
