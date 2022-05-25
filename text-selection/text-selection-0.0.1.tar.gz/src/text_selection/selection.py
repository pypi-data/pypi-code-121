from enum import IntEnum
from typing import Dict, Optional, Set, TypeVar

from ordered_set import OrderedSet

_T1 = TypeVar("_T1")


class SelectionMode(IntEnum):
  FIRST = 0
  LAST = 1
  SHORTEST = 2
  LONGEST = 3


def order_keys(keys: Set[_T1], ordered_keys: OrderedSet[_T1]) -> OrderedSet[_T1]:
  if len(keys) == 0:
    return OrderedSet()
  all_keys_exist = len(keys - ordered_keys) == 0
  assert all_keys_exist
  if len(keys) == 1:
    return OrderedSet(keys)
  result = OrderedSet((key for key in ordered_keys if key in keys))
  return result


def select_key(potential_keys: OrderedSet[_T1], unit_counts: Optional[Dict[_T1, int]], mode: SelectionMode):
  assert isinstance(potential_keys, OrderedSet)
  assert len(potential_keys) > 0
  if len(potential_keys) == 1:
    return potential_keys[0]
  if mode == SelectionMode.FIRST:
    return select_first(potential_keys)
  if mode == SelectionMode.LAST:
    return select_last(potential_keys)
  if mode == SelectionMode.SHORTEST:
    assert unit_counts is not None
    return select_shortest(potential_keys, unit_counts)
  if mode == SelectionMode.LONGEST:
    assert unit_counts is not None
    return select_longest(potential_keys, unit_counts)
  raise Exception()


class KeySelector():
  def select_key(self, keys: OrderedSet[_T1]) -> _T1:
    raise NotImplementedError()


class FirstKeySelector(KeySelector):
  def select_key(self, keys: OrderedSet[_T1]) -> _T1:
    assert isinstance(keys, OrderedSet)
    assert len(keys) > 0
    first = keys[0]
    return first


def select_first(potential_keys: OrderedSet[_T1]) -> _T1:
  assert isinstance(potential_keys, OrderedSet)
  assert len(potential_keys) > 0
  first = potential_keys[0]
  return first


def select_last(potential_keys: OrderedSet[_T1]) -> _T1:
  assert isinstance(potential_keys, OrderedSet)
  assert len(potential_keys) > 0
  first = potential_keys[-1]
  return first


def select_longest(potential_keys: OrderedSet[_T1], data: Dict[_T1, int]) -> _T1:
  assert isinstance(potential_keys, OrderedSet)
  total_counts = []
  for potential_key in potential_keys:
    assert potential_key in data
    utterance_len = data[potential_key]
    total_counts.append((potential_key, utterance_len))
  key, _ = max(total_counts, key=lambda key_count: key_count[1])
  return key


def select_shortest(potential_keys: OrderedSet[_T1], data: Dict[_T1, int]) -> _T1:
  assert isinstance(potential_keys, OrderedSet)
  total_counts = []
  for potential_key in potential_keys:
    assert potential_key in data
    utterance_len = data[potential_key]
    total_counts.append((potential_key, utterance_len))
  key, _ = min(total_counts, key=lambda key_count: key_count[1])
  return key
