"""
A collection of useful classes for handling selections.
"""

from __future__ import annotations

# standard libraries
import copy
import enum
import numbers
import typing

# third party libraries
# None

# local libraries
from nion.utils import Event


class Style(enum.Enum):
    none = 0
    single = 1
    single_or_none = 2
    multiple = 3


class IndexedSelection:
    """Track a selection using integer indexes.

    Supplies many routines for manipulating the selection.

    Fires `changed()` events when the selection changes.

    The `expanded_changed_event` attribute was introduced in 0.3.23 to indicate that it is
    ok to send changed events when the auto adjusting methods `insert_index` or `remove_index`
    are called. Explicitly opting into this behavior is required to maintain backwards
    compatibility. New uses of the class should always set that attribute and it is expected
    to be default behavior in 0.4.0.
    """
    def __init__(self, selection_style: typing.Optional[Style] = None, expanded_changed_event: bool = False) -> None:
        super().__init__()
        self.__changed_event = Event.Event()
        self.expanded_changed_event = expanded_changed_event  # whether to fire when updating indexes
        self.__indexes : typing.MutableSet[int] = set()
        self.__anchor_index : typing.Optional[int] = None
        self.selection_style = selection_style if selection_style else Style.multiple

    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, IndexedSelection) and self.indexes == other.indexes and self.anchor_index == other.anchor_index

    def __ne__(self, other: typing.Any) -> bool:
        return not isinstance(other, IndexedSelection) or self.indexes != other.indexes or self.anchor_index != other.anchor_index

    def __copy__(self) -> IndexedSelection:
        selection = self.__class__(self.selection_style)
        selection.set_multiple(set(self.__indexes))
        selection.anchor_index = self.__anchor_index
        return selection

    def __deepcopy__(self, memo: typing.Dict[typing.Any, typing.Any]) -> IndexedSelection:
        selection = self.__class__(self.selection_style)
        selection.set_multiple(set(self.__indexes))
        selection.anchor_index = self.__anchor_index
        return selection

    @property
    def changed_event(self) -> Event.Event:
        return self.__changed_event

    @property
    def current_index(self) -> typing.Optional[int]:
        if len(self.__indexes) == 1:
            for index in self.__indexes:
                return index
        return None

    @property
    def anchor_index(self) -> typing.Optional[int]:
        return self.__anchor_index

    @anchor_index.setter
    def anchor_index(self, value: typing.Optional[int]) -> None:
        self.__anchor_index = value

    @property
    def has_selection(self) -> bool:
        return len(self.__indexes) > 0

    def contains(self, index: int) -> bool:
        return index in self.__indexes

    @property
    def indexes(self) -> typing.Set[int]:
        return typing.cast(typing.Set[int], copy.copy(self.__indexes))

    @property
    def ordered_indexes(self) -> typing.Sequence[int]:
        indexes = sorted(self.__indexes)
        if len(self.__indexes) > 0 and self.__anchor_index is not None and self.__anchor_index in self.__indexes:
            indexes.remove(self.__anchor_index)
            indexes.insert(0, self.__anchor_index)
        return indexes

    def clear(self) -> None:
        old_index = copy.copy(self.__indexes)
        if self.selection_style == Style.single:
            self.__indexes.add(0)
            self.__anchor_index = 0
        else:
            self.__indexes = set()
            self.__anchor_index = None
        if old_index != self.__indexes:
            self.__fire_changed_event()

    def __fire_changed_event(self) -> None:
        self.__changed_event.fire()

    def __update_anchor_index(self) -> None:
        for index in self.__indexes:
            if self.__anchor_index is None or index < self.__anchor_index:
                self.__anchor_index = index

    def add(self, index: int) -> None:
        assert isinstance(index, numbers.Integral)
        if self.selection_style in (Style.single, Style.single_or_none):
            self.set(index)
        elif self.selection_style in (Style.multiple, ):
            old_index = copy.copy(self.__indexes)
            self.__indexes.add(index)
            if len(old_index) == 0:
                self.__anchor_index = index
            if old_index != self.__indexes:
                self.__fire_changed_event()
        else:
            self.clear()

    def remove(self, index: int) -> None:
        assert isinstance(index, numbers.Integral)
        if self.selection_style in (Style.multiple, Style.single_or_none):
            old_index = copy.copy(self.__indexes)
            self.__indexes.remove(index)
            if not self.__anchor_index in self.__indexes:
                self.__update_anchor_index()
            if old_index != self.__indexes:
                self.__fire_changed_event()
        elif self.selection_style in (Style.single, ):
            pass
        else:
            self.clear()

    def add_range(self, _range: range) -> None:
        for index in _range:
            self.add(index)

    def set_multiple(self, indexes: typing.Set[int]) -> None:
        if self.selection_style in (Style.multiple, ):
            old_index = copy.copy(self.__indexes)
            self.__indexes = set()
            self.__indexes.update(indexes)
            self.__anchor_index = list(indexes)[0] if len(indexes) > 0 else None
            if old_index != self.__indexes:
                self.__fire_changed_event()
        elif self.selection_style in (Style.single, Style.single_or_none) and len(indexes) == 1:
            self.set(list(indexes)[0])
        else:
            self.clear()

    def set(self, index: int) -> None:
        assert isinstance(index, numbers.Integral)
        if self.selection_style in (Style.multiple, Style.single, Style.single_or_none):
            old_index = copy.copy(self.__indexes)
            self.__indexes = set()
            self.__indexes.add(index)
            self.__anchor_index = index
            if old_index != self.__indexes:
                self.__fire_changed_event()
        else:
            self.clear()

    def toggle(self, index: int) -> None:
        assert isinstance(index, numbers.Integral)
        if index in self.__indexes:
            self.remove(index)
        else:
            self.add(index)

    def extend(self, index: int) -> None:
        assert isinstance(index, numbers.Integral)
        if self.selection_style in (Style.multiple, ):
            old_index = copy.copy(self.__indexes)
            if self.__anchor_index is not None:
                if index > self.__anchor_index:
                    for new_index in range(self.__anchor_index, index + 1):
                        self.__indexes.add(new_index)
                elif index < self.__anchor_index:
                    for new_index in range(index, self.__anchor_index + 1):
                        self.__indexes.add(new_index)
            else:
                self.__anchor_index = index
                self.__indexes.add(index)
            if old_index != self.__indexes:
                self.__fire_changed_event()
        elif self.selection_style in (Style.single, Style.single_or_none):
            self.set(index)
        else:
            self.clear()

    def select_forward(self, item_count: int, extend: bool = False, amount: int = 1, wrap: bool = False) -> None:
        new_index = None
        indexes = self.indexes
        if len(indexes) > 0:
            if wrap:
                new_index = (max(indexes) + amount) % item_count
            else:
                new_index = min(max(indexes) + amount, item_count - 1)
        elif item_count > 0:
            # nothing is selected, just select the first item
            new_index = 0
        if new_index is not None:
            if extend:
                self.extend(new_index)
            else:
                self.set(new_index)

    def select_backward(self, item_count: int, extend: bool = False, amount: int = 1, wrap: bool = False) -> None:
        new_index = None
        indexes = self.indexes
        if len(indexes) > 0:
            if wrap:
                new_index = (item_count + min(indexes) - amount) % item_count
            else:
                new_index = max(min(indexes) - amount, 0)
        elif item_count > 0:
            # nothing is selected, just select the last item
            new_index = item_count - 1
        if new_index is not None:
            if extend:
                self.extend(new_index)
            else:
                self.set(new_index)

    def insert_index(self, new_index: int) -> None:
        new_indexes = set()
        for index in self.__indexes:
            if index < new_index:
                new_indexes.add(index)
            else:
                new_indexes.add(index + 1)
        if self.__anchor_index is not None:
            if new_index <= self.__anchor_index:
                self.__anchor_index += 1
        if self.__indexes != new_indexes:
            self.__indexes = new_indexes
            if self.expanded_changed_event:
                self.__fire_changed_event()

    def remove_index(self, remove_index: int) -> None:
        new_indexes = set()
        for index in self.__indexes:
            if index != remove_index:
                if index > remove_index:
                    new_indexes.add(index - 1)
                else:
                    new_indexes.add(index)
        if self.__anchor_index is not None:
            if remove_index == self.__anchor_index:
                self.__update_anchor_index()
            elif remove_index < self.__anchor_index:
                self.__anchor_index -= 1
        if self.__indexes != new_indexes:
            self.__indexes = new_indexes
            if self.expanded_changed_event:
                self.__fire_changed_event()
