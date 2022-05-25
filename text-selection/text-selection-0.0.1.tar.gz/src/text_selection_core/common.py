from dataclasses import dataclass
from typing import Optional

from ordered_set import OrderedSet

from text_selection.selection import FirstKeySelector, SelectionMode
from text_selection_core.types import Dataset, DataWeights, SubsetName, Weight
from text_selection_core.validation import (ValidationErr, ensure_percentual_value_is_valid,
                                            ensure_subsets_are_distinct, ensure_subsets_exist,
                                            ensure_weight_line_count_matches_dataset)


@dataclass()
class WeightSelectionParameters():
  weights: DataWeights
  target: Weight
  target_incl_selection: bool
  target_percent: bool


@dataclass()
class SelectionDefaultParameters():
  dataset: Dataset
  from_subset_names: OrderedSet[SubsetName]
  to_subset_name: SubsetName


@dataclass()
class SortingDefaultParameters():
  dataset: Dataset
  subset_names: OrderedSet[SubsetName]


def validate_selection_default_parameters(params: SelectionDefaultParameters) -> Optional[ValidationErr]:
  # if error := ensure_subsets_exist(params.dataset, params.from_subset_names):
  #   return error

  # if error := SubsetNotExistsError.validate(params.dataset, params.to_subset_name):
  #   return error

  if error := ensure_subsets_are_distinct(params.from_subset_names, params.to_subset_name):
    return error

  return None


def validate_weights_parameters(params: WeightSelectionParameters, dataset: Dataset) -> Optional[ValidationErr]:
  if error := ensure_weight_line_count_matches_dataset(dataset, params.weights):
    return error

  if params.target_percent:
    if error := ensure_percentual_value_is_valid(params.target):
      return error

  return None


def validate_sorting_default_parameters(params: SortingDefaultParameters) -> Optional[ValidationErr]:
  if error := ensure_subsets_exist(params.dataset, params.subset_names):
    return error

  return None


# class NGramsNotExistError(ValidationError):
#   def __init__(self, n_grams: NGramSet) -> None:
#     super().__init__()
#     self.n_grams = n_grams

#   @classmethod
#   def validate(cls, n_grams: NGramSet, ids: Iterable[LineNr]):
#     all_n_grams_exist = all(data_id in n_grams.indices_to_data_ids for data_id in ids)
#     if not all_n_grams_exist:
#       return cls(n_grams)
#     return None

#   @property
#   def default_message(self) -> str:
#     return f"Not all n-grams exist!"


def get_selector(mode: SelectionMode):
  if mode == SelectionMode.FIRST:
    selector = FirstKeySelector()
    return selector
  assert False
