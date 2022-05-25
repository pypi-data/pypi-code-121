from logging import getLogger
from typing import Iterator, Tuple

import numpy as np
from ordered_set import OrderedSet

from text_selection.selection import KeySelector


class GreedyIterator(Iterator[int]):
  def __init__(self, data: np.ndarray, data_indices: OrderedSet[int], preselection: np.ndarray, key_selector: KeySelector) -> None:
    super().__init__()
    self.__data = data
    self.__key_selector = key_selector
    self.__available_data_keys_ordered = data_indices.copy()
    if np.any(preselection == 0, axis=0):
      self.__covered_array = preselection.copy()
    else:
      self.__covered_array = np.zeros_like(preselection)
    self._current_epoch = 0

  def __iter__(self) -> Iterator[int]:
    return self

  @property
  def current_epoch(self) -> int:
    """zero-based epoch"""
    return self._current_epoch

  @property
  def is_fresh_epoch(self) -> bool:
    result = np.all(self.__covered_array == 0, axis=0)
    return result

  @property
  def currently_uncovered(self) -> np.ndarray:
    """returns indices of uncovered columns in the current epoch"""
    result = np.flatnonzero(self.__covered_array == 0)
    return result

  @property
  def currently_covered(self) -> np.ndarray:
    """returns indices of covered columns in the current epoch"""
    result = np.flatnonzero(self.__covered_array)
    return result

  def __next__(self) -> int:
    if len(self.__available_data_keys_ordered) == 0:
      raise StopIteration()

    potential_keys = get_keys_with_most_new(
      data=self.__data,
      keys=self.__available_data_keys_ordered,
      covered_counts=self.__covered_array,
    )

    potential_keys = OrderedSet(potential_keys)

    if len(potential_keys) > 1:
      logger = getLogger(__name__)
      logger.debug(f"Found {len(potential_keys)} candidates for the current iteration.")

    selected_key = self.__key_selector.select_key(potential_keys)
    assert 0 <= selected_key < len(self.__data)
    self.__covered_array += self.__data[selected_key]
    self.__available_data_keys_ordered.remove(selected_key)

    covered_everything = np.all(self.__covered_array > 0, axis=0)
    if covered_everything:
      # reset epoch
      self.__covered_array = np.zeros_like(self.__covered_array)
      self._current_epoch += 1

    return selected_key


def get_keys_with_most_new(data: np.ndarray, keys: OrderedSet[int], covered_counts: np.ndarray) -> Iterator[int]:
  assert len(data.shape) == 2
  assert len(covered_counts.shape) == 1
  assert 0 < len(keys) <= len(data)
  data_subset: np.ndarray = data[keys]
  max_indices = get_indices_with_most_new(data_subset, covered_counts)
  del data_subset
  mapped_indices = (keys[index] for index in max_indices)
  return mapped_indices


def get_indices_with_most_new(data: np.ndarray, covered_counts: np.ndarray) -> np.ndarray:
  data_subset_uncovered = select_uncovered_columns(data, covered_counts)
  uncovered_amounts = get_uncovered_amounts(data_subset_uncovered)
  del data_subset_uncovered
  _, max_indices = get_maximum_indices(uncovered_amounts)
  del _
  del uncovered_amounts
  return max_indices


def select_uncovered_columns(data: np.ndarray, covered_counts: np.ndarray) -> np.ndarray:
  assert len(data.shape) == 2
  assert len(covered_counts.shape) == 1
  assert data.shape[1] == covered_counts.shape[0]
  uncovered_indices = np.flatnonzero(covered_counts == 0)
  data_subset_uncovered_total_counts = data[:, uncovered_indices]
  del uncovered_indices
  return data_subset_uncovered_total_counts


def get_uncovered_amounts(data: np.ndarray) -> np.ndarray:
  data_subset_amounts = data != 0
  uncovered_amounts = np.sum(data_subset_amounts, axis=1)
  del data_subset_amounts
  return uncovered_amounts


def get_maximum_indices(array: np.ndarray) -> Tuple[float, np.ndarray]:
  assert len(array) > 0
  max_value = array.max()
  max_indices = np.flatnonzero(array == max_value)
  return max_value, max_indices
