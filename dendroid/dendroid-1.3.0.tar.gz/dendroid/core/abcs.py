from abc import (ABC,
                 ABCMeta,
                 abstractmethod)
from collections import abc
from copy import deepcopy
from itertools import chain
from typing import (Generic,
                    Iterable,
                    Iterator,
                    List,
                    Optional,
                    TypeVar,
                    Union)

from reprit.base import generate_repr

from .hints import (Item,
                    Key,
                    Value)
from .utils import capacity

NIL = None


class Node(metaclass=ABCMeta):
    __slots__ = 'value',

    left = NIL  # type: Union[NIL, 'Node']
    right = NIL  # type: Union[NIL, 'Node']

    @property
    def item(self) -> Item:
        return self.key, self.value

    @property
    @abstractmethod
    def key(self) -> Key:
        """Comparisons key."""


AnyNode = Union[NIL, Node]


class Tree(ABC, Generic[Key, Value]):
    __slots__ = 'root',

    def __init__(self, root: AnyNode) -> None:
        self.root = root

    def __bool__(self) -> bool:
        """Checks if the tree has nodes."""
        return self.root is not NIL

    def __copy__(self) -> 'Tree[Key, Value]':
        return type(self)(deepcopy(self.root))

    def __iter__(self) -> Iterator[Node]:
        """Returns iterator over nodes in ascending keys order."""
        node = self.root
        queue = []
        while True:
            while node is not NIL:
                queue.append(node)
                node = node.left
            if not queue:
                return
            node = queue.pop()
            yield node
            node = node.right

    def __len__(self) -> int:
        """Returns number of nodes."""
        return capacity(self)

    def __reversed__(self) -> Iterator[Node]:
        """Returns iterator over nodes in descending keys order."""
        node = self.root
        queue = []
        while True:
            while node is not NIL:
                queue.append(node)
                node = node.right
            if not queue:
                return
            node = queue.pop()
            yield node
            node = node.left

    @classmethod
    @abstractmethod
    def from_components(cls,
                        keys: Iterable[Key],
                        values: Optional[Iterable[Value]] = None
                        ) -> 'Tree[Key, Value]':
        """Constructs tree from given components."""

    __repr__ = generate_repr(from_components,
                             with_module_name=True)

    @property
    def keys(self) -> List[Key]:
        return [node.key for node in self]

    @property
    def values(self) -> List[Value]:
        return [node.value for node in self]

    def clear(self) -> None:
        self.root = NIL

    def find(self, key: Key) -> AnyNode:
        """Searches for the node corresponding to a key."""
        node = self.root
        while node is not NIL:
            if key < node.key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                break
        return node

    def infimum(self, key: Key) -> AnyNode:
        """Returns first node with a key not greater than the given one."""
        node, result = self.root, NIL
        while node is not NIL:
            if key < node.key:
                node = node.left
            elif node.key < key:
                result, node = node, node.right
            else:
                result = node
                break
        return result

    @abstractmethod
    def insert(self, key: Key, value: Value) -> AnyNode:
        """Inserts given key-value pair in the tree."""

    def max(self) -> AnyNode:
        """Returns node with the maximum key."""
        node = self.root
        if node is not NIL:
            while node.right is not NIL:
                node = node.right
        return node

    def min(self) -> AnyNode:
        """Returns node with the minimum key."""
        node = self.root
        if node is not NIL:
            while node.left is not NIL:
                node = node.left
        return node

    def pop(self, key: Key) -> AnyNode:
        """Removes node with given key from the tree."""
        node = self.find(key)
        if node is not NIL:
            self.remove(node)
        return node

    def popmin(self) -> AnyNode:
        node = self.root
        if node is not NIL:
            while node.left is not NIL:
                node = node.left
            self.remove(node)
        return node

    def popmax(self) -> AnyNode:
        node = self.root
        if node is not NIL:
            while node.right is not NIL:
                node = node.right
            self.remove(node)
        return node

    @abstractmethod
    def predecessor(self, node: Node) -> AnyNode:
        """Returns last node with a key less than of the given one."""

    @abstractmethod
    def remove(self, node: Node) -> None:
        """Removes node from the tree."""

    @abstractmethod
    def successor(self, node: Node) -> AnyNode:
        """Returns first node with a key greater than of the given one."""

    def supremum(self, key: Key) -> AnyNode:
        """Returns first node with a key not less than the given one."""
        node, result = self.root, NIL
        while node is not NIL:
            if key < node.key:
                result, node = node, node.left
            elif node.key < key:
                node = node.right
            else:
                result = node
                break
        return result


Self = TypeVar('Self')


@abc.Set.register
class AbstractSet(Generic[Value]):
    def __and__(self: Self, other: Self) -> Self:
        """Returns intersection of the set with given one."""
        return (self.from_iterable(value for value in self if value in other)
                if isinstance(other, AbstractSet)
                else NotImplemented)

    @abstractmethod
    def __contains__(self: Self, value: Value) -> bool:
        """Checks if given value is presented in the set."""

    def __eq__(self: Self, other: Self) -> bool:
        """Checks if the set is equal to given one."""
        return (len(self) == len(other) and self <= other <= self
                if isinstance(other, AbstractSet)
                else NotImplemented)

    def __ge__(self: Self, other: Self) -> bool:
        """Checks if the set is a superset of given one."""
        return (len(self) >= len(other)
                and all(value in self for value in other)
                if isinstance(other, AbstractSet)
                else NotImplemented)

    def __gt__(self: Self, other: Self) -> bool:
        """Checks if the set is a strict superset of given one."""
        return (len(self) > len(other)
                and self >= other and self != other
                if isinstance(other, AbstractSet)
                else NotImplemented)

    @abstractmethod
    def __iter__(self: Self) -> Iterator[Value]:
        """Returns iterator over the set values."""

    def __le__(self: Self, other: Self) -> bool:
        """Checks if the set is a subset of given one."""
        return (len(self) <= len(other)
                and all(value in other for value in self)
                if isinstance(other, AbstractSet)
                else NotImplemented)

    @abstractmethod
    def __len__(self: Self) -> int:
        """Returns size of the set."""

    def __lt__(self: Self, other: Self) -> bool:
        """Checks if the set is a strict subset of given one."""
        return (len(self) < len(other)
                and self <= other and self != other
                if isinstance(other, AbstractSet)
                else NotImplemented)

    def __or__(self: Self, other: Self) -> Self:
        """Returns union of the set with given one."""
        return (self.from_iterable(chain(self, other))
                if isinstance(other, AbstractSet)
                else NotImplemented)

    def __sub__(self: Self, other: Self) -> Self:
        """Returns subtraction of the set with given one."""
        return (self.from_iterable(value
                                   for value in self
                                   if value not in other)
                if isinstance(other, AbstractSet)
                else NotImplemented)

    def __xor__(self: Self, other: Self) -> Self:
        """Returns symmetric difference of the set with given one."""
        return ((self - other) | (other - self)
                if isinstance(other, AbstractSet)
                else NotImplemented)

    @abstractmethod
    def from_iterable(self: Self, values: Iterable[Value]) -> Self:
        """Constructs set from given values."""

    def isdisjoint(self: Self, other: Self) -> bool:
        """Checks if the tree has no intersection with given one."""
        return (all(value not in other for value in self)
                if len(self) < len(other)
                else all(value not in self for value in other))


@abc.MutableSet.register
class MutableSet(AbstractSet[Value]):
    def __iand__(self: Self, other: Self) -> Self:
        """Intersects the set with given one in-place."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        for value in self - other:
            self.discard(value)
        return self

    def __ior__(self: Self, other: Self) -> Self:
        """Unites the set with given one in-place."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        for value in other:
            self.add(value)
        return self

    def __isub__(self: Self, other: Self) -> Self:
        """Subtracts from the set a given one in-place."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        if self == other:
            self.clear()
        else:
            for value in other:
                self.discard(value)
        return self

    def __ixor__(self: Self, other: Self) -> Self:
        """Exclusively disjoins the set with given one in-place."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        if self == other:
            self.clear()
        else:
            for value in other:
                if value in self:
                    self.discard(value)
                else:
                    self.add(value)
        return self

    @abstractmethod
    def add(self: Self, value: Value) -> None:
        """Adds given value to the set."""

    @abstractmethod
    def discard(self: Self, value: Value) -> None:
        """Removes given value from the set if it is present."""

    @abstractmethod
    def remove(self: Self, value: Value) -> None:
        """Removes given value that is present in the set."""
