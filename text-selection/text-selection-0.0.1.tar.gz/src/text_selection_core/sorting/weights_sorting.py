from logging import Logger

import numpy as np
from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection_core.common import SortingDefaultParameters, validate_sorting_default_parameters
from text_selection_core.globals import TQDM_LINE_UNIT, ExecutionResult
from text_selection_core.types import DataWeights


def sort_after_weights(default_params: SortingDefaultParameters, weights: DataWeights, logger: Logger) -> ExecutionResult:
  if error := validate_sorting_default_parameters(default_params):
    return error

  changed_anything = False
  for subset_name in default_params.subset_names:
    logger.debug(f"Sorting \"{subset_name}\"...")
    subset = default_params.dataset.subsets[subset_name]

    subset_weights = weights[subset]
    logger.debug("Applying argsort...")
    indices = np.argsort(subset_weights, axis=0)
    logger.debug("Rebuilding index...")
    indices = tqdm(indices, desc="Rebuilding index", unit=TQDM_LINE_UNIT)
    ordered_subset = OrderedSet()
    for index in indices:
      ordered_subset.add(subset[index])

    if ordered_subset != subset:
      default_params.dataset.subsets[subset_name] = ordered_subset
      changed_anything = True
  return changed_anything
