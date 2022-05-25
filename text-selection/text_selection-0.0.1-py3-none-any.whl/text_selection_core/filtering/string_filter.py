import re
from functools import partial
from logging import Logger
from typing import Callable, Generator, Iterator, List, Set

from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection_core.common import (SelectionDefaultParameters,
                                        validate_selection_default_parameters)
from text_selection_core.globals import TQDM_LINE_UNIT, ExecutionResult
from text_selection_core.helper import get_percent_str
from text_selection_core.types import (Line, LineNr, Lines, Subset, get_subsets_line_nrs_count,
                                       get_subsets_line_nrs_gen, move_lines_to_subset)
from text_selection_core.validation import ensure_lines_count_matches_dataset


def filter_by_string(default_params: SelectionDefaultParameters, lines: Lines, starts_with: Set[str], ends_with: Set[str], contains: Set[str], equals: Set[str], mode: str, logger: Logger) -> ExecutionResult:
  if error := validate_selection_default_parameters(default_params):
    return error

  if error := ensure_lines_count_matches_dataset(default_params.dataset, lines):
    return error

  select_from_nrs = get_subsets_line_nrs_gen(
    default_params.dataset, default_params.from_subset_names)
  select_from_count = get_subsets_line_nrs_count(
    default_params.dataset, default_params.from_subset_names)
  result: Subset = OrderedSet()
  select_from_nrs = tqdm(select_from_nrs, total=select_from_count,
                         desc="Filtering", unit=TQDM_LINE_UNIT)

  methods = []
  if equals:
    methods.append(partial(line_equals, equals=equals))

  if starts_with:
    methods.append(partial(line_starts_with, starts_with=starts_with))

  if ends_with:
    methods.append(partial(line_ends_with, ends_with=ends_with))

  if contains:
    methods.append(partial(line_contains, contains=contains))

  assert len(methods) > 0

  query = partial(
    match_line,
    mode=mode,
    methods=methods,
  )

  select_from_nrs = tqdm(select_from_nrs, desc="Filtering",
                         unit=TQDM_LINE_UNIT, total=select_from_count)
  for line_nr in select_from_nrs:
    if query(lines[line_nr]):
      result.add(line_nr)
      logger.info(f"Filtered L-{line_nr+1}: \"{lines[line_nr]}\".")

  changed_anything = False
  if len(result) > 0:
    logger.info(
      f"Filtered {len(result)} out of {select_from_count} lines ({get_percent_str(len(result),select_from_count)}). {select_from_count-len(result)} lines remain.")
    move_lines_to_subset(default_params.dataset, result, default_params.to_subset_name, logger)
    changed_anything = True
  return changed_anything


def match_line(line: Line, mode: str, methods: List[Callable[[str], bool]]) -> bool:
  method_results = (method(line) for method in methods)
  if mode == "all":
    result = all(method_results)
  elif mode == "any":
    result = any(method_results)
  return result


# def line_match(line: Line, mode: str, starts_with: Optional[Set[str]], ends_with: Optional[Set[str]], contains: Optional[Set[str]], equals: Optional[Set[str]]) -> bool:

#   if line_starts_with(line, starts_with):
#     return True

#   if line_ends_with(line, ends_with):
#     return True

#   if line_contains(line, contains):
#     return True

#   if line_equals(line, equals):
#     return True
#   return False


def line_starts_with(line: Line, starts_with: Set[str]) -> bool:
  for s in starts_with:
    if line.startswith(s):
      return True
  return False


def line_ends_with(line: Line, ends_with: Set[str]) -> bool:
  for s in ends_with:
    if line.endswith(s):
      return True
  return False


def line_contains(line: Line, contains: Set[str]) -> bool:
  for s in contains:
    if s in line:
      return True
  return False


def line_equals(line: Line, equals: Set[str]) -> bool:
  for s in equals:
    if line == s:
      return True
  return False


def get_matching_lines(lines: Lines, line_nrs: Iterator[LineNr], pattern: re.Pattern) -> Generator[LineNr, None, None]:
  for line_nr in line_nrs:
    if pattern.match(lines[line_nr]) is not None:
      yield line_nr
