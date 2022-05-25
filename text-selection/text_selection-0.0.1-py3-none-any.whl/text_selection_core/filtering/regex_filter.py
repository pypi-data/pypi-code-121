import re
from logging import Logger
from typing import Generator, Iterator

from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection_core.common import (SelectionDefaultParameters,
                                        validate_selection_default_parameters)
from text_selection_core.globals import TQDM_LINE_UNIT, ExecutionResult
from text_selection_core.helper import get_percent_str
from text_selection_core.types import (LineNr, Lines, Subset, get_subsets_line_nrs_count,
                                       get_subsets_line_nrs_gen, move_lines_to_subset)
from text_selection_core.validation import ensure_lines_count_matches_dataset


def filter_regex_pattern(default_params: SelectionDefaultParameters, lines: Lines, pattern: str, logger: Logger) -> ExecutionResult:
  if error := validate_selection_default_parameters(default_params):
    return error

  if error := ensure_lines_count_matches_dataset(default_params.dataset, lines):
    return error

  select_from_nrs = get_subsets_line_nrs_gen(
    default_params.dataset, default_params.from_subset_names)
  select_from_count = get_subsets_line_nrs_count(
    default_params.dataset, default_params.from_subset_names)
  re_pattern = re.compile(pattern)
  logger.debug(f"Pattern: {re_pattern}")
  
  result: Subset = OrderedSet()
  select_from_nrs = tqdm(select_from_nrs, desc="Filtering",
                         unit=TQDM_LINE_UNIT, total=select_from_count)
  for line_nr in get_matching_lines(lines, select_from_nrs, re_pattern):
    result.add(line_nr)
    logger.info(f"Filtered L-{line_nr+1}: \"{lines[line_nr]}\".")

  changed_anything = False
  if len(result) > 0:
    logger.info(
      f"Filtered {len(result)} out of {select_from_count} lines ({get_percent_str(len(result),select_from_count)}). {select_from_count-len(result)} lines remain.")
    move_lines_to_subset(default_params.dataset, result, default_params.to_subset_name, logger)
    changed_anything = True
  return changed_anything


def get_matching_lines(lines: Lines, line_nrs: Iterator[LineNr], pattern: re.Pattern) -> Generator[LineNr, None, None]:
  for line_nr in line_nrs:
    if pattern.match(lines[line_nr]) is not None:
      yield line_nr
