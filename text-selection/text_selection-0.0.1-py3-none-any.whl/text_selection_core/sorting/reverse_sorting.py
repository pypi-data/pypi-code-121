from logging import Logger
from ordered_set import OrderedSet

from text_selection_core.algorithms.reverse import get_reverse_iterator
from text_selection_core.common import SortingDefaultParameters, validate_sorting_default_parameters
from text_selection_core.globals import ExecutionResult


def sort_reverse(default_params: SortingDefaultParameters, logger: Logger) -> ExecutionResult:
  if error := validate_sorting_default_parameters(default_params):
    return error

  changed_anything = False
  for subset_name in default_params.subset_names:
    subset = default_params.dataset.subsets[subset_name]
    iterator = get_reverse_iterator(subset)
    ordered_subset = OrderedSet(iterator)
    if ordered_subset != subset:
      default_params.dataset.subsets[subset_name] = ordered_subset
      changed_anything = True
  return changed_anything
