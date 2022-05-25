from typing import Dict, List
from typing import OrderedDict as OrderedDictType
from typing import TypeVar

from ordered_set import OrderedSet
from text_selection.greedy.greedy_methods import (get_greedy_cover,
                                                  sort_greedy,
                                                  sort_greedy_epochs,
                                                  sort_greedy_until,
                                                  sort_greedy_until_advanced)
from text_selection.selection import SelectionMode
from text_selection.utils import values_to_set

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def greedy_cover(data: OrderedDictType[_T1, List[_T2]], already_covered: OrderedDictType[_T1, List[_T2]]) -> OrderedSet[_T1]:
  available_set = values_to_set(data)
  already_covered_set = values_to_set(already_covered)
  already_covered_units = {x for y in already_covered_set.values() for x in y}
  result = get_greedy_cover(data=available_set, already_covered=already_covered_units)
  return result


def greedy_seconds(data: OrderedDictType[_T1, List[_T2]], durations_s: Dict[int, float], seconds: float) -> OrderedSet[_T1]:
  available_set = values_to_set(data)
  result = sort_greedy_until(
    data=available_set, until_values=durations_s, until_value=seconds)
  return result


def greedy_duration_advanced(data: OrderedDictType[_T1, List[_T2]], durations: Dict[int, float], target_duration: float, mode: SelectionMode) -> OrderedSet[_T1]:
  result = sort_greedy_until_advanced(
    data=data,
    until_values=durations,
    until_value=target_duration,
    mode=mode,
  )

  return result


def greedy_count(data: OrderedDictType[_T1, List[_T2]], chars: Dict[int, int], total_count: int) -> OrderedSet[_T1]:
  available_set = values_to_set(data)
  result = sort_greedy_until(
    data=available_set, until_values=chars, until_value=total_count)
  return result


def greedy_epochs(data: OrderedDictType[_T1, List[_T2]], epochs: int) -> OrderedSet[_T1]:
  available_set = values_to_set(data)
  result = sort_greedy_epochs(data=available_set, epochs=epochs)
  return result


def greedy_iterations(data: OrderedDictType[_T1, List[_T2]], iterations: int) -> OrderedSet[_T1]:
  # maybe own method in greedy_methods
  greedy_selected = greedy_default(data)
  result = greedy_selected[:iterations]
  return result


def greedy_default(data: OrderedDictType[_T1, List[_T2]]) -> OrderedSet[_T1]:
  # maybe own method in greedy_methods
  available_set = values_to_set(data)
  result = sort_greedy(data=available_set)
  return result
