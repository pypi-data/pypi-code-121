from logging import Logger

from ordered_set import OrderedSet

from text_selection_core.globals import ExecutionResult
from text_selection_core.types import (Dataset, LineNrs, Subset, SubsetName, move_lines_to_subset)
from text_selection_core.validation import ensure_line_nrs_exist


def filter_nrs(dataset: Dataset, to_subset_name: SubsetName, nrs: LineNrs, logger: Logger) -> ExecutionResult:
  if error := ensure_line_nrs_exist(dataset, nrs):
    return error

  if to_subset_name not in dataset.subsets:
    to_subset = OrderedSet()
  else:
    to_subset = dataset.subsets[to_subset_name]

  new_ids = (entry_id for entry_id in nrs if entry_id not in to_subset)
  result: Subset = OrderedSet(new_ids)
  changed_anything = False

  if len(result) > 0:
    logger.info(f"Selected {len(result)} lines.")
    move_lines_to_subset(dataset, result, to_subset_name, logger)
    changed_anything = True

  if len(result) < len(nrs):
    logger.info(f"{len(nrs) - len(result)} were already selected.")

  return changed_anything

