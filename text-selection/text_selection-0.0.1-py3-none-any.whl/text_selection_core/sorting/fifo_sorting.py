from logging import Logger

from ordered_set import OrderedSet

from text_selection_core.algorithms.fifo import get_line_nr_iterator
from text_selection_core.common import SortingDefaultParameters, validate_sorting_default_parameters
from text_selection_core.globals import ExecutionResult


def sort_fifo(default_params: SortingDefaultParameters, logger: Logger) -> ExecutionResult:
  if error := validate_sorting_default_parameters(default_params):
    return error

  changed_anything = False
  for subset_name in default_params.subset_names:
    subset = default_params.dataset.subsets[subset_name]

    original_line_nrs = OrderedSet(default_params.dataset.get_line_nrs())
    iterator = get_line_nr_iterator(subset, original_line_nrs)

    ordered_subset = OrderedSet(iterator)
    if ordered_subset != subset:
      default_params.dataset.subsets[subset_name] = ordered_subset
      changed_anything = True
  return changed_anything
