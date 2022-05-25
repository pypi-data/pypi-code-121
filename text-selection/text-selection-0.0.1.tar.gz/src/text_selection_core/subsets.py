from logging import Logger

from ordered_set import OrderedSet

from text_selection_core.globals import ExecutionResult
from text_selection_core.types import Dataset, SubsetName
from text_selection_core.validation import (ensure_not_only_one_subset_exists, ensure_subset_exists,
                                            ensure_subset_not_already_exists,
                                            ensure_subsets_exist,
                                            ensure_subsets_not_already_exist)


def add_subsets(dataset: Dataset, names: OrderedSet[SubsetName], logger: Logger) -> ExecutionResult:
  if error := ensure_subsets_not_already_exist(dataset, names):
    return error

  for name in names:
    dataset.subsets[name] = OrderedSet()

  return True


def remove_subsets(dataset: Dataset, names: OrderedSet[SubsetName], logger: Logger) -> ExecutionResult:
  if error := ensure_subsets_exist(dataset, names):
    return error

  if error := ensure_not_only_one_subset_exists(dataset):
    return error

  for name in names:
    dataset.subsets.pop(name)

  return True


def rename_subset(dataset: Dataset, name: SubsetName, new_name: SubsetName, logger: Logger) -> ExecutionResult:
  if error := ensure_subset_exists(dataset, name):
    return error

  if error := ensure_subset_not_already_exists(dataset, new_name):
    return error

  dataset.subsets[new_name] = dataset.subsets.pop(name)

  return True
