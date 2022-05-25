from functools import partial
from reprlib import recursive_repr
from typing import (Any,
                    Callable,
                    Iterable,
                    Optional,
                    Tuple,
                    Union)

from reprit.base import generate_repr

from .core.abcs import (NIL,
                        Node as _Node,
                        Tree as _Tree)
from .core.maps import map_constructor as _map_constructor
from .core.sets import set_constructor as _set_constructor
from .core.utils import (dereference_maybe as _dereference_maybe,
                         maybe_weakref as _maybe_weakref,
                         to_balanced_tree_height as _to_balanced_tree_height,
                         to_unique_sorted_items as _to_unique_sorted_items,
                         to_unique_sorted_values as _to_unique_sorted_values)
from .hints import (Key,
                    MapFactory,
                    SetFactory,
                    Value)


class Node(_Node):
    __slots__ = ('_key', 'value', 'is_black', '_parent', '_left', '_right',
                 '__weakref__')

    def __init__(self,
                 key: Key,
                 value: Value,
                 is_black: bool,
                 left: Union[NIL, 'Node'] = NIL,
                 right: Union[NIL, 'Node'] = NIL,
                 parent: Optional['Node'] = None) -> None:
        self._key, self.value, self.is_black = key, value, is_black
        self.left, self.right, self._parent = left, right, parent

    __repr__ = recursive_repr()(generate_repr(__init__))

    State = Tuple[Any, ...]

    def __getstate__(self) -> State:
        return (self._key, self.value, self.is_black,
                self.parent, self._left, self._right)

    def __setstate__(self, state: State) -> None:
        (self._key, self.value, self.is_black,
         self.parent, self._left, self._right) = state

    @classmethod
    def from_simple(cls, key: Key, *args: Any) -> 'Node':
        return cls(key, key, *args)

    @property
    def key(self) -> Key:
        return self._key

    @property
    def left(self) -> Union[NIL, 'Node']:
        return self._left

    @left.setter
    def left(self, node: Union[NIL, 'Node']) -> None:
        self._left = node
        _set_parent(node, self)

    @property
    def parent(self) -> Optional['Node']:
        return _dereference_maybe(self._parent)

    @parent.setter
    def parent(self, node: Optional['Node']) -> None:
        self._parent = _maybe_weakref(node)

    @property
    def right(self) -> Union[NIL, 'Node']:
        return self._right

    @right.setter
    def right(self, node: Union[NIL, 'Node']) -> None:
        self._right = node
        _set_parent(node, self)


def _set_parent(node: Union[NIL, Node], parent: Optional[Node]) -> None:
    if node is not NIL:
        node.parent = parent


def _set_black(maybe_node: Optional[Node]) -> None:
    if maybe_node is not None:
        maybe_node.is_black = True


def _is_left_child(node: Node) -> bool:
    parent = node.parent
    return parent is not None and parent.left is node


def _is_node_black(node: Union[NIL, Node]) -> bool:
    return node is NIL or node.is_black


class Tree(_Tree[Key, Value]):
    @staticmethod
    def predecessor(node: Node) -> Node:
        if node.left is NIL:
            result = node.parent
            while result is not None and node is result.left:
                node, result = result, result.parent
        else:
            result = node.left
            while result.right is not NIL:
                result = result.right
        return result

    @staticmethod
    def successor(node: Node) -> Node:
        if node.right is NIL:
            result = node.parent
            while result is not None and node is result.right:
                node, result = result, result.parent
        else:
            result = node.right
            while result.left is not NIL:
                result = result.left
        return result

    @classmethod
    def from_components(cls,
                        keys: Iterable[Key],
                        values: Optional[Iterable[Value]] = None
                        ) -> 'Tree[Key, Value]':
        keys = list(keys)
        if not keys:
            root = NIL
        elif values is None:
            keys = _to_unique_sorted_values(keys)

            def to_node(start_index: int,
                        end_index: int,
                        depth: int,
                        height: int = _to_balanced_tree_height(len(keys)),
                        constructor: Callable[..., Node] = Node.from_simple
                        ) -> Node:
                middle_index = (start_index + end_index) // 2
                return constructor(
                        keys[middle_index], depth != height,
                        (to_node(start_index, middle_index, depth + 1)
                         if middle_index > start_index
                         else NIL),
                        (to_node(middle_index + 1, end_index, depth + 1)
                         if middle_index < end_index - 1
                         else NIL))

            root = to_node(0, len(keys), 0)
            root.is_black = True
        else:
            items = _to_unique_sorted_items(keys, tuple(values))

            def to_node(start_index: int,
                        end_index: int,
                        depth: int,
                        height: int = _to_balanced_tree_height(len(items)),
                        constructor: Callable[..., Node] = Node) -> Node:
                middle_index = (start_index + end_index) // 2
                return constructor(
                        *items[middle_index], depth != height,
                        (to_node(start_index, middle_index, depth + 1)
                         if middle_index > start_index
                         else NIL),
                        (to_node(middle_index + 1, end_index, depth + 1)
                         if middle_index < end_index - 1
                         else NIL))

            root = to_node(0, len(items), 0)
            root.is_black = True
        return cls(root)

    def insert(self, key: Key, value: Value) -> Node:
        parent = self.root
        if parent is NIL:
            node = self.root = Node(key, value, True)
            return node
        while True:
            if key < parent.key:
                if parent.left is NIL:
                    node = Node(key, value, False)
                    parent.left = node
                    break
                else:
                    parent = parent.left
            elif parent.key < key:
                if parent.right is NIL:
                    node = Node(key, value, False)
                    parent.right = node
                    break
                else:
                    parent = parent.right
            else:
                return parent
        self._restore(node)
        return node

    def remove(self, node: Node) -> None:
        successor, is_node_black = node, node.is_black
        if successor.left is NIL:
            (successor_child, successor_child_parent,
             is_successor_child_left) = (successor.right, successor.parent,
                                         _is_left_child(successor))
            self._transplant(successor, successor_child)
        elif successor.right is NIL:
            (successor_child, successor_child_parent,
             is_successor_child_left) = (successor.left, successor.parent,
                                         _is_left_child(successor))
            self._transplant(successor, successor_child)
        else:
            successor = node.right
            while successor.left is not NIL:
                successor = successor.left
            is_node_black = successor.is_black
            successor_child, is_successor_child_left = successor.right, False
            if successor.parent is node:
                successor_child_parent = successor
            else:
                is_successor_child_left = _is_left_child(successor)
                successor_child_parent = successor.parent
                self._transplant(successor, successor.right)
                successor.right = node.right
            self._transplant(node, successor)
            successor.left, successor.left.parent = node.left, successor
            successor.is_black = node.is_black
        if is_node_black:
            self._remove_node_fixup(successor_child, successor_child_parent,
                                    is_successor_child_left)

    def _restore(self, node: Node) -> None:
        while not _is_node_black(node.parent):
            parent = node.parent
            grandparent = parent.parent
            if parent is grandparent.left:
                uncle = grandparent.right
                if _is_node_black(uncle):
                    if node is parent.right:
                        self._rotate_left(parent)
                        node, parent = parent, node
                    parent.is_black, grandparent.is_black = True, False
                    self._rotate_right(grandparent)
                else:
                    parent.is_black = uncle.is_black = True
                    grandparent.is_black = False
                    node = grandparent
            else:
                uncle = grandparent.left
                if _is_node_black(uncle):
                    if node is parent.left:
                        self._rotate_right(parent)
                        node, parent = parent, node
                    parent.is_black, grandparent.is_black = True, False
                    self._rotate_left(grandparent)
                else:
                    parent.is_black = uncle.is_black = True
                    grandparent.is_black = False
                    node = grandparent
        self.root.is_black = True

    def _remove_node_fixup(self, node: Union[NIL, Node], parent: Node,
                           is_left_child: bool) -> None:
        while node is not self.root and _is_node_black(node):
            if is_left_child:
                sibling = parent.right
                if not _is_node_black(sibling):
                    sibling.is_black, parent.is_black = True, False
                    self._rotate_left(parent)
                    sibling = parent.right
                if (_is_node_black(sibling.left)
                        and _is_node_black(sibling.right)):
                    sibling.is_black = False
                    node, parent = parent, parent.parent
                    is_left_child = _is_left_child(node)
                else:
                    if _is_node_black(sibling.right):
                        sibling.left.is_black, sibling.is_black = True, False
                        self._rotate_right(sibling)
                        sibling = parent.right
                    sibling.is_black, parent.is_black = parent.is_black, True
                    _set_black(sibling.right)
                    self._rotate_left(parent)
                    node = self.root
            else:
                sibling = parent.left
                if not _is_node_black(sibling):
                    sibling.is_black, parent.is_black = True, False
                    self._rotate_right(parent)
                    sibling = parent.left
                if (_is_node_black(sibling.left)
                        and _is_node_black(sibling.right)):
                    sibling.is_black = False
                    node, parent = parent, parent.parent
                    is_left_child = _is_left_child(node)
                else:
                    if _is_node_black(sibling.left):
                        sibling.right.is_black, sibling.is_black = True, False
                        self._rotate_left(sibling)
                        sibling = parent.left
                    sibling.is_black, parent.is_black = parent.is_black, True
                    _set_black(sibling.left)
                    self._rotate_right(parent)
                    node = self.root
        _set_black(node)

    def _rotate_left(self, node: Node) -> None:
        replacement = node.right
        self._transplant(node, replacement)
        node.right, replacement.left = replacement.left, node

    def _rotate_right(self, node: Node) -> None:
        replacement = node.left
        self._transplant(node, replacement)
        node.left, replacement.right = replacement.right, node

    def _transplant(self, origin: Node, replacement: Union[NIL, Node]) -> None:
        parent = origin.parent
        if parent is None:
            self.root = replacement
            _set_parent(replacement, None)
        elif origin is parent.left:
            parent.left = replacement
        else:
            parent.right = replacement


map_ = partial(_map_constructor, Tree.from_components)  # type: MapFactory
set_ = partial(_set_constructor, Tree.from_components)  # type: SetFactory
