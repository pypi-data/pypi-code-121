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
                        AnyNode,
                        Node as _Node,
                        Tree as _Tree)
from .core.maps import map_constructor as _map_constructor
from .core.sets import set_constructor as _set_constructor
from .core.utils import (dereference_maybe as _dereference_maybe,
                         maybe_weakref as _maybe_weakref,
                         to_unique_sorted_items as _to_unique_sorted_items,
                         to_unique_sorted_values as _to_unique_sorted_values)
from .hints import (Key,
                    MapFactory,
                    SetFactory,
                    Value)


class Node(_Node):
    __slots__ = ('_key', 'value', 'height', '_parent', '_left', '_right',
                 '__weakref__')

    def __init__(self,
                 key: Key,
                 value: Value,
                 left: Union[NIL, 'Node'] = NIL,
                 right: Union[NIL, 'Node'] = NIL,
                 parent: Optional['Node'] = None) -> None:
        self._key, self.value = key, value
        self.left, self.right, self.parent = left, right, parent
        self.height = max(_to_height(self._left), _to_height(self._right)) + 1

    __repr__ = recursive_repr()(generate_repr(__init__))

    State = Tuple[Any, ...]

    def __getstate__(self) -> State:
        return (self._key, self.value, self.height,
                self.parent, self._left, self._right)

    def __setstate__(self, state: State) -> None:
        (self._key, self.value, self.height,
         self.parent, self._left, self._right) = state

    @classmethod
    def from_simple(cls, key: Key, *args: Any) -> 'Node':
        return cls(key, key, *args)

    @property
    def balance_factor(self) -> int:
        return _to_height(self.left) - _to_height(self.right)

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


def _to_height(node: Union[NIL, Node]) -> int:
    return -1 if node is NIL else node.height


def _update_height(node: Node) -> None:
    node.height = max(_to_height(node.left), _to_height(node.right)) + 1


def _set_parent(node: Union[NIL, Node],
                parent: Optional[Node]) -> None:
    if node is not NIL:
        node.parent = parent


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
    def successor(node: Node) -> AnyNode:
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
                        constructor: Callable[..., Node] = Node.from_simple
                        ) -> Node:
                middle_index = (start_index + end_index) // 2
                return constructor(keys[middle_index],
                                   (to_node(start_index, middle_index)
                                    if middle_index > start_index
                                    else NIL),
                                   (to_node(middle_index + 1, end_index)
                                    if middle_index < end_index - 1
                                    else NIL))

            root = to_node(0, len(keys))
        else:
            items = _to_unique_sorted_items(keys, list(values))

            def to_node(start_index: int,
                        end_index: int,
                        constructor: Callable[..., Node] = Node) -> Node:
                middle_index = (start_index + end_index) // 2
                return constructor(*items[middle_index],
                                   (to_node(start_index, middle_index)
                                    if middle_index > start_index
                                    else NIL),
                                   (to_node(middle_index + 1, end_index)
                                    if middle_index < end_index - 1
                                    else NIL))

            root = to_node(0, len(items))
        return cls(root)

    def insert(self, key: Key, value: Value) -> Node:
        parent = self.root
        if parent is NIL:
            node = self.root = Node(key, value)
            return node
        while True:
            if key < parent.key:
                if parent.left is NIL:
                    node = Node(key, value)
                    parent.left = node
                    break
                else:
                    parent = parent.left
            elif parent.key < key:
                if parent.right is NIL:
                    node = Node(key, value)
                    parent.right = node
                    break
                else:
                    parent = parent.right
            else:
                return parent
        self._rebalance(node.parent)
        return node

    def remove(self, node: Node) -> None:
        if node.left is NIL:
            imbalanced_node = node.parent
            self._transplant(node, node.right)
        elif node.right is NIL:
            imbalanced_node = node.parent
            self._transplant(node, node.left)
        else:
            successor = node.right
            while successor.left is not NIL:
                successor = successor.left
            if successor.parent is node:
                imbalanced_node = successor
            else:
                imbalanced_node = successor.parent
                self._transplant(successor, successor.right)
                successor.right = node.right
            self._transplant(node, successor)
            successor.left, successor.left.parent = node.left, successor
        self._rebalance(imbalanced_node)

    def _rebalance(self, node: Node) -> None:
        while node is not None:
            _update_height(node)
            if node.balance_factor > 1:
                if node.left.balance_factor < 0:
                    self._rotate_left(node.left)
                self._rotate_right(node)
            elif node.balance_factor < -1:
                if node.right.balance_factor > 0:
                    self._rotate_right(node.right)
                self._rotate_left(node)
            node = node.parent

    def _rotate_left(self, node: Node) -> None:
        replacement = node.right
        self._transplant(node, replacement)
        node.right, replacement.left = replacement.left, node
        _update_height(node)
        _update_height(replacement)

    def _rotate_right(self, node: Node) -> None:
        replacement = node.left
        self._transplant(node, replacement)
        node.left, replacement.right = replacement.right, node
        _update_height(node)
        _update_height(replacement)

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
