from logging import getLogger
from typing import Dict, Set

import numpy as np
from ordered_set import OrderedSet
from text_selection.utils import DurationBoundary
from tqdm import tqdm


def get_duration_keys(durations: Dict[int, float], keys: Set[int], boundary: DurationBoundary) -> OrderedSet[int]:
  logger = getLogger(__name__)
  all_keys_exist_in_durations = len(durations.keys() - keys) == 0
  assert all_keys_exist_in_durations
  boundary_min, boundary_max = boundary
  logger.info("Getting entries maching duration boundary...")
  filtered_utterance_ids = get_keys_in_duration_boundary(
    durations, keys, boundary_min, boundary_max)
  not_selected_utterances_out_of_boundary = len(keys) - len(filtered_utterance_ids)

  if not_selected_utterances_out_of_boundary > 0:
    logger.warning(
        f"Missed out utterances due to duration boundary [{boundary_min},{boundary_max}): {not_selected_utterances_out_of_boundary}/{len(keys)} ({not_selected_utterances_out_of_boundary/len(keys)*100:.2f}%) -> retrieved {len(filtered_utterance_ids)} entries.")
  else:
    logger.debug(
      f"Didn't missed out any utterances through boundary [{boundary_min},{boundary_max}) -> kept {len(filtered_utterance_ids)} entries.")

  return filtered_utterance_ids


def get_keys_in_duration_boundary(corpus: Dict[int, float], keys: OrderedSet[int], min_duration_incl: float, max_duration_excl: float) -> OrderedSet[int]:
  assert min_duration_incl >= 0
  assert max_duration_excl >= 0

  filtered_utterance_indicies: OrderedSet[int] = OrderedSet()

  for utterance_id in tqdm(keys):
    assert utterance_id in corpus
    utterance_duration = corpus[utterance_id]
    if min_duration_incl <= utterance_duration < max_duration_excl:
      filtered_utterance_indicies.add(utterance_id)

  return filtered_utterance_indicies


def get_duration_keys_np(durations: np.ndarray, boundary: DurationBoundary) -> OrderedSet[int]:
  logger = getLogger(__name__)
  boundary_min, boundary_max = boundary
  logger.info("Getting entries maching duration boundary...")
  filtered_utterance_ids = get_indices_in_duration_boundary(
    durations, boundary_min, boundary_max)
  not_selected_utterances_out_of_boundary = len(durations) - len(filtered_utterance_ids)

  if not_selected_utterances_out_of_boundary > 0:
    logger.warning(
        f"Missed out utterances due to duration boundary [{boundary_min},{boundary_max}): {not_selected_utterances_out_of_boundary}/{len(durations)} ({not_selected_utterances_out_of_boundary/len(durations)*100:.2f}%) -> retrieved {len(filtered_utterance_ids)} entries.")
  else:
    logger.debug(
      f"Didn't missed out any utterances through boundary [{boundary_min},{boundary_max}) -> kept {len(filtered_utterance_ids)} entries.")

  result = OrderedSet(filtered_utterance_ids)
  return result


def get_indices_in_duration_boundary(data: np.ndarray, min_duration_incl: float, max_duration_excl: float) -> np.ndarray:
  assert min_duration_incl >= 0
  assert max_duration_excl >= 0
  result = np.where((min_duration_incl <= data) & (data < max_duration_excl))[0]
  #
  return result
