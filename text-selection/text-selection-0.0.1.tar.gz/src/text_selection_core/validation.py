from abc import abstractmethod
from enum import IntEnum
from typing import Optional

from ordered_set import OrderedSet

from text_selection_core.types import Dataset, DataWeights, LineNrs, Lines, SubsetName


class ErrorType(IntEnum):
  LINES_MISMATCH = 0
  WEIGHTS_LINES_MISMATCH = 1
  SUBSET_ALREADY_EXISTS = 2
  IS_LAST_SUBSET = 3
  SUBSET_NOT_EXIST = 4
  INVALID_PERCENT = 5
  NON_DISTINCT_SUBSETS = 6
  LINE_NRS_NOT_EXIST = 7


_DEFAULT_ERROR_PATTERNS = {
  ErrorType.LINES_MISMATCH:
    "Line count does not match with dataset lines count ({0} vs. {1})!",
  ErrorType.WEIGHTS_LINES_MISMATCH:
    "Weights dimension does not match with dataset lines count ({0} vs. {1})!",
  ErrorType.SUBSET_ALREADY_EXISTS:
    "The subset \"{0}\" already exists!",
  ErrorType.IS_LAST_SUBSET:
    "The last subset could not be removed!",
  ErrorType.SUBSET_NOT_EXIST:
    "The subset \"{0}\" does not exist!",
  ErrorType.INVALID_PERCENT:
    "The percentual value \"{0}\" is invalid, it needs to be between in interval (0, 100]!",
  ErrorType.NON_DISTINCT_SUBSETS:
    "The subsets need to be distinct!",
  ErrorType.LINE_NRS_NOT_EXIST:
    "The line number(s) {0} do(es) not exist in the dataset!",
}


class ValidationErrBase():
  @property
  @abstractmethod
  def default_message(self) -> str:
    ...


class ValidationErr(ValidationErrBase):
  def __init__(self, error_type: ErrorType, *msg_args: object) -> None:
    super().__init__()
    self.__error_type = error_type
    self.__args = msg_args

  @property
  def default_message(self) -> str:
    result = str.format(_DEFAULT_ERROR_PATTERNS[self.__error_type], *self.__args)
    return result

  @property
  def error_type(self) -> ErrorType:
    return self.__error_type

  @property
  def msg_args(self) -> object:
    return self.__args


def ensure_weight_line_count_matches_dataset(dataset: Dataset, weights: DataWeights) -> Optional[ValidationErr]:
  if len(weights) != dataset.line_count:
    return ValidationErr(ErrorType.WEIGHTS_LINES_MISMATCH, len(weights), dataset.line_count)
  return None


def ensure_lines_count_matches_dataset(dataset: Dataset, lines: Lines) -> Optional[ValidationErr]:
  if len(lines) != dataset.line_count:
    return ValidationErr(ErrorType.LINES_MISMATCH, len(lines), dataset.line_count)
  return None


def ensure_subset_not_already_exists(dataset: Dataset, subset: SubsetName) -> Optional[ValidationErr]:
  if subset in dataset.subsets:
    return ValidationErr(ErrorType.SUBSET_ALREADY_EXISTS, subset)
  return None


def ensure_subsets_not_already_exist(dataset: Dataset, subsets: OrderedSet[SubsetName]) -> Optional[ValidationErr]:
  for subset in subsets:
    if error := ensure_subset_not_already_exists(dataset, subset):
      return error
  return None


def ensure_subset_exists(dataset: Dataset, subset: SubsetName) -> Optional[ValidationErr]:
  if subset not in dataset.subsets:
    return ValidationErr(ErrorType.SUBSET_NOT_EXIST, subset)
  return None


def ensure_subsets_exist(dataset: Dataset, subsets: OrderedSet[SubsetName]) -> Optional[ValidationErr]:
  for subset in subsets:
    if error := ensure_subset_exists(dataset, subset):
      return error
  return None


def ensure_not_only_one_subset_exists(dataset: Dataset) -> Optional[ValidationErr]:
  if len(dataset) == 1:
    return ValidationErr(ErrorType.IS_LAST_SUBSET)
  return None


def ensure_percentual_value_is_valid(percent: float) -> Optional[ValidationErr]:
  if not 0 < percent <= 100:
    return ValidationErr(ErrorType.INVALID_PERCENT, percent)
  return None


def ensure_subsets_are_distinct(from_subset_names: OrderedSet[SubsetName], to_subset_name: SubsetName) -> Optional[ValidationErr]:
  for from_subset_name in from_subset_names:
    if from_subset_name == to_subset_name:
      return ValidationErr(ErrorType.NON_DISTINCT_SUBSETS)
  return None


def ensure_line_nrs_exist(dataset: Dataset, line_nrs: LineNrs) -> Optional[ValidationErr]:
  missing_line_nrs = line_nrs.difference(dataset.get_line_nrs())
  if len(missing_line_nrs) > 0:
    missing_line_nrs_str = ', '.join(missing_line_nrs)
    return ValidationErr(ErrorType.LINE_NRS_NOT_EXIST, missing_line_nrs_str)
  return None
