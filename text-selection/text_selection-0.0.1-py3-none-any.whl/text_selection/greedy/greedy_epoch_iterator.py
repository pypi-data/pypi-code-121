from typing import Iterator

from text_selection.greedy.greedy_iterator import GreedyIterator


class EpochProxyIterator(Iterator[int]):
  def __init__(self, iterator: GreedyIterator, epochs: int) -> None:
    assert epochs >= 0
    self.__iterator = iterator
    self.__epochs = epochs
    self.__update_progress = 0
    self.__enough_data_was_available = True

  @property
  def tqdm_update(self) -> int:
    return self.__update_progress

  @property
  def was_enough_data_available(self) -> bool:
    return self.__enough_data_was_available

  @property
  def target_epochs(self) -> int:
    return self.__epochs

  def __iter__(self) -> Iterator[int]:
    return self

  def __next__(self) -> int:
    if self.__iterator.current_epoch == self.__epochs:
      raise StopIteration()

    current_epoch = self.__iterator.current_epoch
    # note: raises exception if more data is not available
    try:
      result = next(self.__iterator)
    except StopIteration:
      self.__enough_data_was_available = False
      raise StopIteration()

    started_next_epoch = self.__iterator.current_epoch == current_epoch + 1
    if started_next_epoch:
      self.__update_progress = 1
    else:
      self.__update_progress = 0
    return result
