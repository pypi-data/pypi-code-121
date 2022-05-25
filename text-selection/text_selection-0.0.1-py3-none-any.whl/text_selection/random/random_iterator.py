import random
from typing import Iterator

from ordered_set import OrderedSet


class RandomIterator(Iterator[int]):
  def __init__(self, data_indices: OrderedSet[int], seed: int) -> None:
    super().__init__()
    assert isinstance(data_indices, OrderedSet)
    self.__available_data_keys_ordered = data_indices.copy()
    random.seed(seed)

  def __iter__(self) -> Iterator[int]:
    return self

  def __next__(self) -> int:
    if len(self.__available_data_keys_ordered) == 0:
      raise StopIteration()

    next_index = random.choice(self.__available_data_keys_ordered)
    self.__available_data_keys_ordered.remove(next_index)
    return next_index
