from logging import Logger

from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection_core.common import SortingDefaultParameters, validate_sorting_default_parameters
from text_selection_core.globals import TQDM_LINE_UNIT, ExecutionResult
from text_selection_core.types import Lines
from text_selection_core.validation import ensure_lines_count_matches_dataset


def sort_after_text(default_params: SortingDefaultParameters, lines: Lines, logger: Logger) -> ExecutionResult:
  if error := validate_sorting_default_parameters(default_params):
    return error

  if error := ensure_lines_count_matches_dataset(default_params.dataset, lines):
    return error

  changed_anything = False
  for subset_name in default_params.subset_names:
    logger.debug(f"Sorting \"{subset_name}\"...")
    subset = default_params.dataset.subsets[subset_name]

    line_nrs = tqdm(subset, desc="Detecting lines", unit=TQDM_LINE_UNIT)
    subset_lines = [lines[line_nr] for line_nr in line_nrs]
    tmp = zip(subset, subset_lines)
    tmp = sorted(tmp, key=lambda idx_str: idx_str[1], reverse=False)
    ordered_subset, _ = zip(*tmp)
    ordered_subset = OrderedSet(ordered_subset)

    if ordered_subset != subset:
      default_params.dataset.subsets[subset_name] = ordered_subset
      changed_anything = True
  return changed_anything
