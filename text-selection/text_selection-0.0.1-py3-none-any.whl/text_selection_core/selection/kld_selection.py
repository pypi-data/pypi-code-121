from dataclasses import dataclass
from logging import Logger
from typing import Optional

import numpy as np
from ordered_set import OrderedSet
from tqdm import tqdm

from text_selection.common.mapping_iterator import map_indices
from text_selection.kld.custom_kld_iterator import CustomKldIterator
from text_selection.kld.kld_iterator import get_uniform_weights
from text_selection.selection import SelectionMode
from text_selection_core.common import (SelectionDefaultParameters, WeightSelectionParameters,
                                        get_selector, validate_selection_default_parameters,
                                        validate_weights_parameters)
from text_selection_core.globals import ExecutionResult
from text_selection_core.helper import get_initial_weights, get_target_weights_from_percent
from text_selection_core.selection.symbol_extractor import get_array_mp
from text_selection_core.types import Lines, Subset, get_subsets_line_nrs_gen, move_lines_to_subset
from text_selection_core.validation import ensure_lines_count_matches_dataset
from text_selection_core.weights.weights_iterator import WeightsIterator


@dataclass()
class KldSelectionParameters():
  lines: Lines
  ssep: str
  consider_to_subset: bool
  id_selection: SelectionMode


def select_kld(default_params: SelectionDefaultParameters, params: KldSelectionParameters, weight_params: WeightSelectionParameters, chunksize: int, n_jobs: int, maxtasksperchild: Optional[int], logger: Logger) -> ExecutionResult:
  if error := validate_selection_default_parameters(default_params):
    return error

  if error := validate_weights_parameters(weight_params, default_params.dataset):
    return error

  if error := ensure_lines_count_matches_dataset(default_params.dataset, params.lines):
    return error

  from_line_nrs = OrderedSet(get_subsets_line_nrs_gen(default_params.dataset,
                                                      default_params.from_subset_names))

  # if error := NGramsNotExistError.validate(params.lines, from_ids):
  #   return error, False

  calc_line_nrs = from_line_nrs.copy()

  from_ids_mapping = dict(enumerate(from_line_nrs))

  if default_params.to_subset_name in default_params.dataset.subsets:
    to_line_nrs = default_params.dataset.subsets[default_params.to_subset_name]
  else:
    to_line_nrs = OrderedSet()

  if params.consider_to_subset:

    to_ids_mapping = dict(enumerate(to_line_nrs, start=len(calc_line_nrs)))
    calc_line_nrs.update(to_line_nrs)

  data, symbols = get_array_mp(params.lines, calc_line_nrs,
                               params.ssep, logger, chunksize, n_jobs, maxtasksperchild)

  if params.consider_to_subset:
    # if error := NGramsNotExistError.validate(params.lines, from_ids):
    #   return error, False
    assert to_ids_mapping is not None
    preselection_data = data[list(to_ids_mapping.keys())]
    summed_preselection_counts = np.sum(preselection_data, axis=0)
  else:
    summed_preselection_counts = np.zeros(data.shape[1])

  data_indices = OrderedSet(from_ids_mapping.keys())
  selector = get_selector(params.id_selection)

  kld_weights = get_uniform_weights(data.shape[1])

  kld_iterator = CustomKldIterator(
    data=data,
    data_indices=data_indices,
    preselection=summed_preselection_counts,
    key_selector=selector,
    weights=kld_weights,
  )

  initial_weights = get_initial_weights(
    to_line_nrs, weight_params.weights, weight_params.target_incl_selection)

  if weight_params.target_percent:
    weight_params.target = get_target_weights_from_percent(
        from_line_nrs, to_line_nrs, weight_params.weights, weight_params.target, weight_params.target_incl_selection)

  mapping_iterator = map_indices(kld_iterator, from_ids_mapping)
  weights_iterator = WeightsIterator(
    mapping_iterator, weight_params.weights, weight_params.target, initial_weights, logger)

  result: Subset = OrderedSet()
  with tqdm(desc="KLD iterations", unit="it") as greedy_pbar:
    with tqdm(desc="Selecting weight", unit="it", total=weights_iterator.target_weight, initial=weights_iterator.current_weight) as pbar:
      for line_nr in weights_iterator:
        result.add(line_nr)
        logger.info(f"Selected L-{line_nr+1}: \"{params.lines[line_nr]}\".")
        pbar.update(weights_iterator.tqdm_update)
        greedy_pbar.update()

  changed_anything = False

  if not weights_iterator.was_enough_data_available:
    warning = f"Not enough data was available! Stopped with a Kullback-Leibler distance of {kld_iterator.current_kld}."
    logger.warning(warning)
  else:
    logger.info(f"Final Kullback-Leibler distance: {kld_iterator.previous_kld}")

  if len(result) > 0:
    logger.info(f"Selected {len(result)} lines.")
    move_lines_to_subset(default_params.dataset, result, default_params.to_subset_name, logger)
    changed_anything = True
  else:
    logger.info("Didn't selected anything!")

  return changed_anything
