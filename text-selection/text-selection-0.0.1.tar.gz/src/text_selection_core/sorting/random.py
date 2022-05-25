
from text_selection_core.common import SortingDefaultParameters, validate_sorting_default_parameters
from text_selection_core.globals import ExecutionResult


def sort_random(params: SortingDefaultParameters) -> ExecutionResult:
  if error := validate_sorting_default_parameters(params):
    return error

  for subset_name in params.subset_names:
    subset = params.dataset.subsets[subset_name]
    # TODO
    raise NotImplementedError()
    ordered_subset = subset
    params.dataset.subsets[subset_name] = ordered_subset
