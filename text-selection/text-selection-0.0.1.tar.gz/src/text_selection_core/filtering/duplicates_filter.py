from logging import Logger, getLogger
from typing import Optional

from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection_core.common import (SelectionDefaultParameters,
                                        validate_selection_default_parameters)
from text_selection_core.globals import TQDM_LINE_UNIT, ExecutionResult
from text_selection_core.helper import get_percent_str
from text_selection_core.types import (Lines, Subset, get_subsets_line_nrs_count,
                                       get_subsets_line_nrs_gen, move_lines_to_subset)
from text_selection_core.validation import ensure_lines_count_matches_dataset


def filter_duplicates(default_params: SelectionDefaultParameters, lines: Lines, logger: Optional[Logger]) -> ExecutionResult:
  if logger is None:
    logger = getLogger(__name__)

  if error := validate_selection_default_parameters(default_params):
    return error

  if error := ensure_lines_count_matches_dataset(default_params.dataset, lines):
    return error

  select_from_line_nrs = get_subsets_line_nrs_gen(
    default_params.dataset, default_params.from_subset_names)
  select_from_count = get_subsets_line_nrs_count(
    default_params.dataset, default_params. from_subset_names)

  result: Subset = OrderedSet()
  collected = set()
  line_nrs = tqdm(select_from_line_nrs, desc="Filtering duplicates",
                  unit=TQDM_LINE_UNIT, total=select_from_count)
  for line_nr in line_nrs:
    item = lines[line_nr]
    if item in collected:
      result.add(line_nr)
      logger.info(f"Filtered L-{line_nr+1}: \"{lines[line_nr]}\".")
    else:
      collected.add(item)
  del collected

  if changed_anything := len(result) > 0:
    logger.info(
      f"Filtered {len(result)} out of {select_from_count} lines ({get_percent_str(len(result),select_from_count)}). {select_from_count-len(result)} lines remain.")
    move_lines_to_subset(default_params.dataset, result, default_params.to_subset_name, logger)
  else:
    logger.info("No duplicate lines exist!")

  return changed_anything
