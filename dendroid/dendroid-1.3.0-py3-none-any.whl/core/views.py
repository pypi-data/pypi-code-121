from collections import abc
from typing import (Generic,
                    Iterable,
                    Iterator)

from reprit.base import generate_repr

from .abcs import (NIL,
                   AbstractSet,
                   Self,
                   Tree)
from .hints import (Item,
                    Key,
                    Value)
from .utils import split_items


@abc.Sized.register
class BaseView:
    __slots__ = 'tree',

    def __init__(self, tree: Tree) -> None:
        self.tree = tree

    __repr__ = generate_repr(__init__)

    def __len__(self) -> int:
        return len(self.tree)


class ItemsView(BaseView, AbstractSet[Item]):
    def __contains__(self, item: Item) -> bool:
        key, value = item
        node = self.tree.find(key)
        return node is not NIL and node.value == value

    def __iter__(self) -> Iterator[Item]:
        for node in self.tree:
            yield node.item

    def __reversed__(self) -> Iterator[Item]:
        for node in reversed(self.tree):
            yield node.item

    def from_iterable(self: Self, iterable: Iterable[Item]) -> Self:
        keys, values = split_items(list(iterable))
        return ItemsView(self.tree.from_components(keys, values))


class KeysView(BaseView, AbstractSet[Key]):
    def __contains__(self, key: Key) -> bool:
        return self.tree.find(key) is not NIL

    def __iter__(self) -> Iterator[Key]:
        for node in self.tree:
            yield node.key

    def __reversed__(self) -> Iterator[Key]:
        for node in reversed(self.tree):
            yield node.key

    def from_iterable(self: Self, values: Iterable[Key]) -> Self:
        return KeysView(self.tree.from_components(values))


class ValuesView(BaseView, Generic[Value]):
    def __contains__(self, value: Value) -> bool:
        return any(candidate == value for candidate in self)

    def __iter__(self) -> Iterator[Value]:
        for node in self.tree:
            yield node.value

    def __reversed__(self) -> Iterator[Value]:
        for node in reversed(self.tree):
            yield node.value
