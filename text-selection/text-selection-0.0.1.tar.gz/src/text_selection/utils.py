import math
import random
from collections import Counter, OrderedDict
from logging import getLogger
from typing import Dict, List, Optional
from typing import OrderedDict as OrderedDictType
from typing import Set, Tuple, TypeVar, Union

import numpy as np
from ordered_set import OrderedSet
from tqdm import tqdm

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

DurationBoundary = Tuple[float, float]


def get_ngrams(sentence_symbols: List[str], n: int) -> List[Tuple[str]]:
  # TODO: import from text-utils
  if n < 1:
    raise Exception()

  res: List[Tuple[str]] = []
  for i in range(len(sentence_symbols) - n + 1):
    tmp = tuple(sentence_symbols[i:i + n])
    res.append(tmp)
  return res


def get_chunksize(data_count: int, n_jobs: int, chunksize: Optional[int], batches: Optional[int]) -> int:
  if batches is None:
    assert chunksize is not None
    assert chunksize > 0
    return chunksize

  if data_count == 0:
    return 1

  chunksize = math.ceil(data_count / n_jobs / batches)
  return chunksize


def get_filtered_list(l: List[_T1], take_only: Set[_T1]) -> List[_T1]:
  res = [x for x in l if x in take_only]
  return res


def filter_ngrams(ngrams: List[Tuple[_T2]], ignore_symbol_ids: Set[_T1]) -> List[Tuple]:
  res = [x for x in ngrams if len(set(x).intersection(ignore_symbol_ids)) == 0]
  return res


def values_to_set(d: OrderedDictType[_T1, _T2]) -> OrderedDictType[_T1, _T2]:
  res: OrderedDictType[_T1, _T2] = OrderedDict([(k, set(v)) for k, v in d.items()])
  return res


def get_until_sum_set(d: OrderedSet[_T1], until_values: Dict[_T1, Union[float, int]], until_value: Union[float, int]) -> Tuple[OrderedSet[_T1], Union[float, int]]:
  total = 0
  res: OrderedSet[_T1] = OrderedSet()
  for k in d:
    current_val = until_values[k]
    include = total + current_val <= until_value
    if not include:
      break
    res.add(k)
    total += current_val

  return res, total


def filter_after_duration(corpus: Dict[_T1, float], min_duration_incl: float, max_duration_excl: float) -> Set[_T1]:
  assert min_duration_incl >= 0
  assert max_duration_excl >= 0

  filtered_utterance_indicies = set()

  for utterance_id, utterance_duration in tqdm(corpus.items()):
    if min_duration_incl <= utterance_duration < max_duration_excl:
      filtered_utterance_indicies.add(utterance_id)

  return filtered_utterance_indicies


def get_random_subset_indices(sample_set_list: List[Set[int]], n: int) -> List[Set[int]]:
  chosen_indices = random.sample(range(len(sample_set_list)), n)
  while len(set(chosen_indices)) != n:
    chosen_indices = random.sample(range(len(sample_set_list)), n)
  # chosen_sets = [sample_set_list[i] for i in range(len(sample_set_list)) if i in chosen_indices]
  return chosen_indices


def get_chosen_sets(sample_set_list: List[Set[int]], chosen_indices: Set[int]) -> List[Set[int]]:
  ordered_chosen_indices = sorted(list(chosen_indices))
  chosen_sets = [sample_set_list[index] for index in ordered_chosen_indices]
  return chosen_sets


def get_common_durations(chosen_sets: List[Set[int]], durations_s: OrderedDictType[int, float]) -> Dict[Tuple[int, int], float]:
  com_duration_dict = {}
  for i in range(len(chosen_sets)):
    for j in range(i + 1, len(chosen_sets)):
      com_indices = list_of_common_elements_for_one_index(chosen_sets, i, j)
      durs_of_com_indices = [durations_s[index] for index in com_indices]
      com_duration_dict[(i, j)] = np.sum(durs_of_com_indices)
  return com_duration_dict


def list_of_common_elements_for_one_index(chosen_sets: List[Set[int]], index_1: int, index_2) -> List[int]:
  common_index_list = chosen_sets[index_1] & chosen_sets[index_2]
  return common_index_list


def get_top_n(data: OrderedDictType[int, List[_T1]], top_percent: float) -> OrderedSet[_T1]:
  """
  if the distribution is same then it will take the _T1 by ascending sorting to make it deterministic
  """
  distr = get_distribution(data)
  top_n = round(len(distr) * top_percent)
  distr_sorted_after_key = OrderedDict(sorted(distr.items(), key=lambda x: x[0], reverse=False))
  distr_sorted = OrderedDict(sorted(distr_sorted_after_key.items(),
                                    key=lambda x: x[1], reverse=True))
  top_ngrams: OrderedSet[_T1] = OrderedSet(list(distr_sorted.keys())[:top_n])
  return top_ngrams


def get_distribution(ngrams: Dict[_T1, List[_T2]]) -> Dict[_T2, float]:
  ngrams_counter = Counter(x for y in ngrams.values() for x in y)
  vals = list(ngrams_counter.values())
  sum_vals = sum(vals)
  distr: Dict[_T2, float] = {k: v / sum_vals for k, v in ngrams_counter.items()}
  return distr


def get_reverse_distribution(ngrams: Dict[_T1, List[_T2]]) -> Dict[_T2, float]:
  ngrams_counter = Counter(x for y in ngrams.values() for x in y)
  keys_sorted = list(sorted(ngrams_counter.keys()))
  od = OrderedDict([(k, ngrams_counter[k]) for k in keys_sorted])
  vals = list(od.values())
  sum_vals = sum(vals)
  distr: Dict[_T2, float] = {k: vals[i] / sum_vals for i, k in enumerate(reversed(keys_sorted))}
  return distr


def get_filtered_ngrams(data: OrderedDictType[_T1, List[str]], n_gram: int, ignore_symbols: Optional[Set[_T2]]) -> OrderedDictType[_T1, List[Tuple[_T2, ...]]]:
  assert isinstance(data, OrderedDict)

  logger = getLogger(__name__)
  logger.info(f"Calculating {n_gram}-grams...")
  available_ngrams: OrderedDictType[int, List[Tuple]] = OrderedDict([
    (k, get_ngrams(v, n_gram)) for k, v in tqdm(data.items())
  ])

  occurring_symbols = {x for y in data.values() for x in y}
  occurring_symbols_count = len(occurring_symbols)
  occurring_ngrams = {x for y in available_ngrams.values() for x in y}
  occurring_ngrams_count = len(occurring_ngrams)

  logger.info(
      f"Theoretically, the maximum amount of unique {n_gram}-grams is: {occurring_symbols_count ** n_gram}.")

  if occurring_symbols_count > 0:
    logger.info(
      f"The amount of unique occurring {n_gram}-grams is: {occurring_ngrams_count} ({occurring_ngrams_count/(occurring_symbols_count ** n_gram)*100:.2f}%).")

  if ignore_symbols is not None:
    occuring_ignore_symbols = occurring_symbols.intersection(ignore_symbols)

    if len(occuring_ignore_symbols) > 0:
      logger.info(
        f"Removing {n_gram}-grams which contain: {' '.join(list(sorted(occuring_ignore_symbols)))}...")
      available_ngrams: OrderedDictType[int, List[Tuple]] = OrderedDict([
        (k, filter_ngrams(v, occuring_ignore_symbols)) for k, v in available_ngrams.items()
      ])

      new_occurring_ngrams = {x for y in available_ngrams.values() for x in y}
      new_occurring_ngrams_count = len(new_occurring_ngrams)

      logger.info(
          f"Removed {occurring_ngrams_count - new_occurring_ngrams_count} unique {n_gram}-gram(s).")
      logger.info(
        f"Remaining symbols: {' '.join(sorted(occurring_symbols.difference(occuring_ignore_symbols)))}")
    else:
      logger.info("Didn't ignoring any symbols.")
  return available_ngrams


def filter_data_durations(data: OrderedDictType[_T1, List[Tuple[_T2, ...]]], durations: Dict[_T1, float], boundary: DurationBoundary) -> OrderedDictType[int, List[Tuple[_T2, ...]]]:
  logger = getLogger(__name__)
  boundary_min, boundary_max = boundary
  filtered_utterance_ids = filter_after_duration(durations, boundary_min, boundary_max)
  not_selected_utterances_out_of_boundary = len(data) - len(filtered_utterance_ids)

  if not_selected_utterances_out_of_boundary > 0:
    logger.warning(
        f"Missed out utterances due to duration boundary [{boundary_min},{boundary_max}): {not_selected_utterances_out_of_boundary}/{len(data)} ({not_selected_utterances_out_of_boundary/len(data)*100:.2f}%) -> retrieved {len(filtered_utterance_ids)} entries.")
  else:
    logger.debug(
      f"Didn't missed out any utterances through boundary [{boundary_min},{boundary_max}) -> kept {len(filtered_utterance_ids)} entries.")

  result = OrderedDict([(k, v) for k, v in data.items() if k in filtered_utterance_ids])
  return result


def filter_data_durations_number_inplace(data: OrderedDictType[_T1, Tuple[int, ...]], durations: Dict[_T1, float], boundary: DurationBoundary) -> None:
  logger = getLogger(__name__)
  boundary_min, boundary_max = boundary
  filtered_utterance_ids = filter_after_duration(durations, boundary_min, boundary_max)
  not_selected_utterances_out_of_boundary = len(data) - len(filtered_utterance_ids)

  if not_selected_utterances_out_of_boundary > 0:
    logger.warning(
        f"Missed out utterances due to duration boundary [{boundary_min},{boundary_max}): {not_selected_utterances_out_of_boundary}/{len(data)} ({not_selected_utterances_out_of_boundary/len(data)*100:.2f}%) -> retrieved {len(filtered_utterance_ids)} entries.")
  else:
    logger.debug(
      f"Didn't missed out any utterances through boundary [{boundary_min},{boundary_max}) -> kept {len(filtered_utterance_ids)} entries.")

  logger.info("Removing...")
  remove = set(data.keys()) - filtered_utterance_ids
  for utterance_id in tqdm(remove):
    data.pop(utterance_id)


def get_first_percent(data: OrderedSet, percent: float) -> OrderedSet:
  proportion = len(data) / 100 * percent
  # rounding is strange see: https://docs.python.org/3/library/functions.html#round
  percent_count = round(proportion)
  res = data[:percent_count]
  return res


def get_n_divergent_seconds(durations_s: OrderedDictType[_T1, float], seconds: float, n: int) -> List[OrderedSet[_T1]]:
  assert all(np.array(list(durations_s.values())) <= seconds)
  total_dur = sum(durations_s.values())
  assert seconds <= total_dur
  dur_to_fill = n * seconds
  stack_times = math.ceil(dur_to_fill / total_dur)
  data_keys = list(durations_s.keys())
  data_keys *= stack_times
  step_length = round(total_dur / n)

  selected, _ = get_until_sum_set(
      data_keys, until_values=durations_s, until_value=seconds)
  res: List[OrderedSet[_T1]] = [selected]

  for _ in range(n - 1):
    start_index = get_next_start_index(step_length, durations_s, list(res[-1]), data_keys)
    selected, _ = get_until_sum_set(
      data_keys[start_index:], until_values=durations_s, until_value=seconds)
    res.append(selected)
  return res


def log_mp_params(n_jobs: int, chunksize: int, maxtasksperchild: Optional[int], data_count: int) -> None:
  logger = getLogger(__name__)
  logger.info(
    f"Using {n_jobs} processes with chunks of size {chunksize} for {data_count} items and maxtask per child: {maxtasksperchild}.")


def get_next_start_index(step_length: int, durations_s: OrderedDictType[_T1, float], prev_vec: List[_T1], data_keys: List[_T1]) -> int:
  """
  start_index should reference the element in data_keys which has a distance of at least step_length to the first element
  in prev_vec (i.e., it has a distance of exactly step_length or is the first element for which this distance is exceeded.)
  "Distance" in this case is defined as the sum of the durations from prev_vec's second element to the element for which the
  distance to the first element in prev_vec is computed. If no element in prev_vec has a distance >= step_length to the first
  element in prev_vec, the index of the next element in data_keys is returned.

  Example 1: step_length = 4
       durations = {0: 1, 1: 2, 2: 3, 3: 1, 4: 1, 5: 2, 6: 2}
       prev_vec = [0, 1, 2, 3]
       We are looking for the Element in {0,...,6} which has a distance of at least 4 to the element 0
       In this case it is 2, as distance(0,2) = dur(1) + dur (2) = 2 + 3 > 4

  Example 2: step_length = 4
          durations = {index: 1 for index in range(8)}
          prev_vec = [0, 1, 2, 3]
          data_keys = [0, 1, 2, 3, 4, 5, 6, 7]
          Here we have dur(1) + dur(2) + dur(3) < 4, so the index of the element following 3 in data_keys is returned (which is 4)
  """
  assert len(prev_vec) > 0
  assert len(data_keys) > 0
  dur_sum = 0
  index = 0
  while dur_sum < step_length:
    index += 1
    if index == len(prev_vec):
      prev_element = prev_vec[-1]
      start_index = data_keys.index(prev_element) + 1
      return start_index
    dur_sum += durations_s[prev_vec[index]]
  start_element = prev_vec[index]
  start_index = data_keys.index(start_element)
  return start_index


# def ignore_ngrams(available_ngrams: OrderedDictType[int, List[Tuple]], ignore_symbols: Set[str]):
#   logger = getLogger(__name__)
#   if len(ignore_symbols) > 0:
#     occurring_ngrams = {x for y in available_ngrams.values() for x in y}
#     occurring_ngrams_count = len(occurring_ngrams)
#     logger.info(
#       f"Removing entries which contain any of these symbols: {' '.join(list(sorted(ignore_symbols)))}...")
#     available_ngrams: OrderedDictType[int, List[Tuple]] = OrderedDict({
#       k: filter_ngrams(v, ignore_symbols) for k, v in available_ngrams.items()
#     })

#     new_occurring_ngrams = {x for y in available_ngrams.values() for x in y}
#     new_occurring_ngrams_count = len(new_occurring_ngrams)
#     logger.info(
#         f"Removed {occurring_ngrams_count - new_occurring_ngrams_count} unique {n_gram}-gram(s).")
