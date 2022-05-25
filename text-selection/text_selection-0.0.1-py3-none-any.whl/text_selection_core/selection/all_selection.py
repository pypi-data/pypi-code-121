from logging import Logger

from ordered_set import OrderedSet

from text_selection_core.common import (SelectionDefaultParameters,
                                        validate_selection_default_parameters)
from text_selection_core.globals import ExecutionResult
from text_selection_core.types import (get_subsets_line_nrs, move_lines_to_subset)


def select_all(default_params: SelectionDefaultParameters, logger: Logger) -> ExecutionResult:
  if error := validate_selection_default_parameters(default_params):
    return error

  result = OrderedSet(get_subsets_line_nrs(default_params.dataset,
                                           default_params.from_subset_names))

  if len(result) > 0:
    logger.info(f"Selected {len(result)} lines.")
    move_lines_to_subset(default_params.dataset, result, default_params.to_subset_name, logger)
    changed_anything = True
  else:
    logger.info("Didn't selected anything!")

  return changed_anything
