import math
from collections import Counter
from dataclasses import dataclass
from logging import Logger
from typing import Literal, Union

import numpy as np
from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection_core.common import (SelectionDefaultParameters,
                                        validate_selection_default_parameters)
from text_selection_core.globals import TQDM_LINE_UNIT, ExecutionResult
from text_selection_core.helper import get_int_dtype_from_n, get_percent_str, split_adv
from text_selection_core.types import (Lines, Subset, get_subsets_line_nrs_count, get_subsets_line_nrs_gen,
                                       move_lines_to_subset)
from text_selection_core.validation import ensure_lines_count_matches_dataset


@dataclass()
class CountFilterParameters():
  lines: Lines
  ssep: str
  from_incl: Union[int, float]
  to_excl: Union[int, float]
  count_whole: bool
  boundary_percent: bool
  mode: Literal["all", "any"]


def filter_lines_with_unit_frequencies(default_params: SelectionDefaultParameters, params: CountFilterParameters, logger: Logger) -> ExecutionResult:
  if error := validate_selection_default_parameters(default_params):
    return error

  if error := ensure_lines_count_matches_dataset(default_params.dataset, params.lines):
    return error

  select_from_nrs = list(get_subsets_line_nrs_gen(
    default_params.dataset, default_params.from_subset_names))

  select_from_count = get_subsets_line_nrs_count(
    default_params.dataset, default_params.from_subset_names)

  if params.count_whole:
    line_nrs_to_count = default_params.dataset.get_line_nrs()
    line_nrs_to_count_total = len(line_nrs_to_count)
  else:
    line_nrs_to_count = select_from_nrs

  # units = (
  #   unit
  #   for line_nr in line_nrs_to_count
  #   for unit in split_adv(params.lines[line_nr], params.ssep)
  # )

  # counter = Counter(tqdm(units, desc="Calculating counts", unit=" unit(s)"))

  # counters: Dict[LineNr, Counter] = {}
  total_counter = Counter()
  for line_nr in tqdm(line_nrs_to_count, desc="Calculating counts", unit=TQDM_LINE_UNIT, total=line_nrs_to_count_total):
    # line_counts = Counter(split_adv(params.lines[line_nr], params.ssep))
    total_counter.update(split_adv(params.lines[line_nr], params.ssep))
    # counters[line_nr] = line_counts

  # for counter in tqdm(counters.values(), desc="Summing counts", unit=TQDM_LINE_UNIT):

  most_common_word, most_common_occ = total_counter.most_common(1)[0]
  logger.debug(f"Most common word: {most_common_word} (#{most_common_occ})")

  to_count_excl = params.to_excl
  from_count_incl = params.from_incl

  if params.boundary_percent:
    if params.from_incl > 0 or params.to_excl < 100:
      logger.debug("Creating array from counts...")
      occurrences = np.array(tuple(total_counter.values()),
                             dtype=get_int_dtype_from_n(most_common_occ))

    if params.from_incl > 0:
      from_count_incl = np.percentile(occurrences, params.from_incl, axis=0)
      #to_count = params.to_count_excl / 100 * most_common_occ
      from_count_incl = math.floor(from_count_incl)
      logger.info(f"Chosen {from_count_incl} as inclusive lower bound.")
    else:
      from_count_incl = 0

    if params.to_excl < 100:
      to_count_excl = np.percentile(occurrences, params.to_excl, axis=0)
      #to_count = params.to_count_excl / 100 * most_common_occ
      to_count_excl = math.ceil(to_count_excl)
      logger.info(f"Chosen {to_count_excl} as exclusive upper bound.")
    else:
      to_count_excl = math.inf
  else:
    from_count_incl = params.from_incl
    to_count_excl = params.to_excl

  if from_count_incl == to_count_excl - 1 and from_count_incl == 0:
    logger.info("Zero occurrences is not possible therefore nothing can be selected!")
    return False

  if from_count_incl == to_count_excl:
    logger.info("Upper and lower bound are equal therefore nothing can be selected!")
    return False

  if params.mode == "all":
    method = np.all
  elif params.mode == "any":
    method = np.any
  else:
    assert False

  min_max_counts = np.zeros((select_from_count, 2), dtype=get_int_dtype_from_n(most_common_occ))

  select_from_nrs_tqdm = tqdm(select_from_nrs, desc="Filtering", unit=TQDM_LINE_UNIT)
  for line_index, line_nr in enumerate(select_from_nrs_tqdm):
    # counts = counters[line_nr]
    units = split_adv(params.lines[line_nr], params.ssep)
    word_counts = {total_counter[unit] for unit in units}
    min_max_counts[line_index, 0] = min(word_counts)
    min_max_counts[line_index, 1] = max(word_counts)

  logger.debug("Filtering with numpy...")
  #res = min_max_counts[from_count_incl <= min_max_counts < to_count_excl]
  a = method(from_count_incl <= min_max_counts, axis=1)
  b = method(min_max_counts < to_count_excl, axis=1)
  d = np.flatnonzero(a & b)
  del a
  del b

  selected_line_nrs = (select_from_nrs[line_index] for line_index in d)
  selected_line_nrs_tqdm = tqdm(
    selected_line_nrs, desc="Getting line numbers", unit=TQDM_LINE_UNIT, total=len(d))

  result: Subset = OrderedSet()
  for line_nr in selected_line_nrs_tqdm:
    result.add(line_nr)
    logger.info(f"Filtered L-{line_nr+1}: \"{params.lines[line_nr]}\".")
  del d

  # a = np.flatnonzero(from_count_incl <= min_max_counts)
  # b = np.flatnonzero(min_max_counts < to_count_excl)
  # x = np.any((from_count_incl <= min_max_counts) & (min_max_counts < to_count_excl), axis=0)
  # res = np.flatnonzero(x, axis=1)
  # match = method(from_count_incl <= count < to_count_excl for count in word_counts)
  # if match:
  #   result.add(line_nr)
  #   logger.info(f"Filtered L-{line_nr+1}: \"{params.lines[line_nr]}\".")

  changed_anything = False
  if len(result) > 0:
    logger.info(
      f"Filtered {len(result)} out of {len(select_from_nrs)} lines ({get_percent_str(len(result),len(select_from_nrs))}). {len(select_from_nrs)-len(result)} lines remain.")
    move_lines_to_subset(default_params.dataset, result, default_params.to_subset_name, logger)
    changed_anything = True
  return changed_anything
