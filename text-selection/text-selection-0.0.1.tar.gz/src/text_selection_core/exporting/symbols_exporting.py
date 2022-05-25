from logging import Logger
from typing import Optional, Union

from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection_core.globals import TQDM_LINE_UNIT
from text_selection_core.helper import get_percent_str
from text_selection_core.types import (Dataset, Lines, SubsetName, get_subsets_line_nrs_count,
                                       get_subsets_line_nrs_gen)
from text_selection_core.validation import (ValidationErr, ensure_lines_count_matches_dataset,
                                            ensure_subsets_exist)


def export_subset(dataset: Dataset, subset_names: OrderedSet[SubsetName], lines: Lines, lsep: str, logger: Logger) -> Union[Optional[ValidationErr], str]:
  if error := ensure_subsets_exist(dataset, subset_names):
    return error

  if error := ensure_lines_count_matches_dataset(dataset, lines):
    return error

  select_from_nrs = get_subsets_line_nrs_gen(
    dataset, subset_names)
  select_from_count = get_subsets_line_nrs_count(
    dataset, subset_names)

  selected_lines = (
    lines[line_nr]
    for line_nr in select_from_nrs
  )

  selected_lines = tqdm(selected_lines, desc="Rejoining lines",
                        unit=TQDM_LINE_UNIT, total=select_from_count)
  result = lsep.join(selected_lines)
  logger.info(f"Exported {select_from_count} out of all {dataset.line_count} lines ({get_percent_str(select_from_count, dataset.line_count)}). {dataset.line_count-select_from_count} lines were not exported.")

  return result
