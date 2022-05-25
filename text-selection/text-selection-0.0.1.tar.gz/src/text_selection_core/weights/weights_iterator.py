from logging import Logger
from typing import Iterator

from text_selection_core.types import DataWeights, LineNr, Weight


class WeightsIterator(Iterator[LineNr]):
  def __init__(self, iterator: Iterator[LineNr], weights: DataWeights, target: Weight, initial_weight: Weight, logger: Logger) -> None:
    assert initial_weight >= 0
    super().__init__()
    self.__iterator = iterator
    self.__weights = weights
    self.__target = target
    self.__current_total = initial_weight
    self.__enough_data_was_available = True
    self.__update_progress = initial_weight
    self.__logger = logger

  @property
  def tqdm_update(self) -> int:
    return self.__update_progress

  @property
  def target_weight(self) -> bool:
    return self.__target

  @property
  def current_weight(self) -> bool:
    return self.__current_total

  @property
  def was_enough_data_available(self) -> bool:
    return self.__enough_data_was_available

  def __iter__(self) -> Iterator[int]:
    return self

  def __next__(self) -> int:
    if self.__current_total > self.__target:
      self.__logger.debug("Target is overreached. Stopped.")
      raise StopIteration()

    if self.__current_total == self.__target:
      self.__logger.debug("Target is reached. Stopped.")
      raise StopIteration()

    try:
      selected_line_nr = next(self.__iterator)
    except StopIteration:
      self.__enough_data_was_available = False
      self.__logger.debug("Not enough data was available; target was not reached. Stopped.")
      raise StopIteration()

    assert 0 <= selected_line_nr < len(self.__weights)
    selected_weight = self.__weights[selected_line_nr]
    self.__logger.debug(f"Selected weight: {selected_weight}")
    new_total = self.__current_total + selected_weight
    if new_total <= self.__target:
      self.__current_total = new_total
      self.__update_progress = selected_weight
      return selected_line_nr

    self.__logger.debug(f"Weight exceeds target ({self.__target}). Stopped.")
    raise StopIteration()
