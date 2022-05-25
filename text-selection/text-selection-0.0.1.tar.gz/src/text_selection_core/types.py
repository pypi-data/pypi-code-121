from collections import OrderedDict
from logging import Logger
from typing import Generator, List
from typing import OrderedDict as OrderedDictType
from typing import Union

import numpy as np
from ordered_set import OrderedSet

# zero-based line number
LineNr = int
LineNrs = OrderedSet[LineNr]
Line = str
Lines = List[Line]

# 0-100
Percent = float
Weight = Union[float, int]
DataWeights = np.ndarray

Subset = LineNrs
SubsetName = str


def get_line_nrs(line_count) -> range:
  return range(line_count)


class Dataset():
  def __init__(self, line_count: int, default_subset_name: str):
    super().__init__()
    self.__line_count = line_count
    self.__subsets: OrderedDictType[SubsetName, Subset] = OrderedDict((
      (default_subset_name, OrderedSet(get_line_nrs(line_count))),
    ))

  @property
  def line_count(self) -> int:
    return self.__line_count

  @property
  def subsets(self) -> OrderedDictType[SubsetName, Subset]:
    return self.__subsets

  def get_line_nrs(self) -> range:
    return get_line_nrs(self.__line_count)


def create_subset_if_it_not_exists(dataset: Dataset, name: SubsetName, logger: Logger) -> bool:
  if name not in dataset.subsets:
    dataset.subsets[name] = OrderedSet()
    logger.debug(f"Created subset \"{name}\".")
    return True
  return False


def move_lines_to_subset(dataset: Dataset, nrs: LineNrs, target: SubsetName, logger: Logger) -> None:
  logger.debug("Adjusting selection...")
  create_subset_if_it_not_exists(dataset, target, logger)
  target_subset = dataset.subsets[target]
  logger.debug("Update target...")
  target_subset.update(nrs)
  logger.debug("Update subsets...")
  potential_subsets = (dataset.subsets[subset] for subset in dataset.subsets if subset != target)
  for subset in potential_subsets:
    subset.difference_update(nrs)
  logger.debug("Done.")


def get_subsets_line_nrs_gen(dataset: Dataset, subsets: OrderedSet[SubsetName]) -> Generator[LineNr, None, None]:
  from_subsets = (dataset.subsets[from_subset_name] for from_subset_name in subsets)
  lines = (line for subset in from_subsets for line in subset)
  return lines


def get_subsets_line_nrs_count(dataset: Dataset, subsets: OrderedSet[SubsetName]) -> int:
  result = sum(len(dataset.subsets[from_subset_name]) for from_subset_name in subsets)
  return result


def get_subsets_line_nrs(dataset: Dataset, subsets: OrderedSet[SubsetName]) -> Subset:
  result = OrderedSet()
  if len(subsets) == 0:
    return result

  for subset in subsets:
    result.update(dataset.subsets[subset])
  return result
