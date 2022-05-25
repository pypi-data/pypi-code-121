from typing import Iterator, Union

import numpy as np


class UntilProxyIterator(Iterator[int]):
  def __init__(self, iterator: Iterator[int], until_values: np.ndarray, until_value: Union[int, float]) -> None:
    super().__init__()
    self.__iterator = iterator
    self.__until_values = until_values
    self.__until_value = until_value
    self.__current_total = 0.0
    self.__enough_data_was_available = True
    self.__update_progress = 0

  @property
  def tqdm_update(self) -> int:
    return self.__update_progress

  @property
  def was_enough_data_available(self) -> bool:
    return self.__enough_data_was_available

  def __iter__(self) -> Iterator[int]:
    return self

  def __next__(self) -> int:
    if self.__current_total == self.__until_value:
      raise StopIteration()

    try:
      selected_key = next(self.__iterator)
    except StopIteration:
      self.__enough_data_was_available = False
      raise StopIteration()

    assert 0 <= selected_key < len(self.__until_values)
    selected_until_value = self.__until_values[selected_key]
    new_total = self.__current_total + selected_until_value
    if new_total <= self.__until_value:
      self.__current_total = new_total
      self.__update_progress = selected_until_value
      return selected_key
    else:
      raise StopIteration()
