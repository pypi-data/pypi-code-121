from logging import getLogger
from typing import Iterable, Iterator

import numpy as np
from ordered_set import OrderedSet
from text_selection.kld.optimized_kld_iterator import OptimizedKldIterator
from text_selection.selection import KeySelector


class CustomKldIterator(OptimizedKldIterator):
  def __init__(self, data: np.ndarray, data_indices: OrderedSet[int], preselection: np.ndarray, weights: np.ndarray, key_selector: KeySelector) -> None:
    empty_row_indices = get_empty_row_indices(data)
    empty_rows_exist = len(empty_row_indices) > 0
    if empty_rows_exist:
      logger = getLogger(__name__)
      logger.info(
        f"Moving {len(empty_row_indices)} empty row(s) out of {len(data)} rows to the end...")
      data_indices = data_indices.copy()
      remove_from_ordered_set_inplace(data_indices, empty_row_indices)
      logger.info("Done.")
    self.__available_empty_row_indices = OrderedSet(empty_row_indices)
    del empty_row_indices
    self.non_empty_finished = False
    super().__init__(
      data=data,
      preselection=preselection,
      data_indices=data_indices,
      weights=weights,
      key_selector=key_selector,
    )

  def __iter__(self) -> Iterator[int]:
    return self

  def __next__(self) -> int:
    if not self.non_empty_finished:
      try:
        return super().__next__()
      except StopIteration:
        self.non_empty_finished = True

    if len(self.__available_empty_row_indices) > 0:
      selected_key = self.__get_next_empty_row()
      self.__available_empty_row_indices.remove(selected_key)
      self._previous_kld = self.current_kld
      return selected_key
    else:
      raise StopIteration()

  def __get_next_empty_row(self):
    selected_key = self._key_selector.select_key(self.__available_empty_row_indices)
    assert 0 <= selected_key < len(self._data)
    assert np.sum(self._data[selected_key], axis=0) == 0
    return selected_key


def get_empty_row_indices(array: np.ndarray) -> np.ndarray:
  empty_entry_ids = np.where(~array.any(axis=1))[0]
  return empty_entry_ids


def remove_from_ordered_set_inplace(s: OrderedSet[int], indices: Iterable[int]) -> None:
  for index in reversed(sorted(indices)):
    assert 0 <= index < len(s)
    remove_entry = s[index]
    s.remove(remove_entry)
