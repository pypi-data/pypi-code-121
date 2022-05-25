import math
from collections import Counter, OrderedDict
from logging import getLogger
from multiprocessing import Pool
from typing import Dict, List, Optional
from typing import OrderedDict as OrderedDictType
from typing import Set, Tuple, TypeVar, Union

import numpy as np
from ordered_set import OrderedSet
from scipy.stats import entropy
from tqdm import tqdm, trange

from text_selection.selection import (SelectionMode, order_keys, select_first,
                                      select_key)

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def split_into_equal_parts(keys: OrderedSet[_T1], parts_count: int) -> List[OrderedSet[_T1]]:
  assert parts_count > 0
  if len(keys) == 0:
    return []

  chunk_size = math.ceil(len(keys) / parts_count)

  result = [keys[i:i + chunk_size] for i in range(0, len(keys), chunk_size)]

  return result


# def split_into_equal_parts_diverse_lengths_per_set(keys: OrderedSet[_T1], parts_count: int) -> List[OrderedSet[_T1]]:
#   assert parts_count > 0
#   tmp: OrderedDictType[int, OrderedSet[_T1]] = OrderedDict({
#     part_id: OrderedSet() for part_id in range(parts_count)
#   })

#   current_part_id = 0
#   for key in keys:
#     tmp[current_part_id].add(key)
#     current_part_id += 1
#     if current_part_id == parts_count:
#       current_part_id = 0
#   result = list(tmp.values())
#   return result


def get_keys_sort_after_value(data: OrderedDictType[_T1, Union[int, float]]) -> OrderedSet[_T1]:
  # required to have predictable results when equal entries exist in values
  assert isinstance(data, OrderedDict)
  if len(data) == 0:
    return OrderedSet()
  sorted_keys, _ = list(zip(*sorted(data.items(), key=lambda kv: kv[1])))
  result = OrderedSet(sorted_keys)
  return result


# def apply_sorting(sorted_keys: OrderedSet[_T1], data: Dict[_T1, _T2]) -> OrderedDictType[_T1, _T2]:
#   assert set(sorted_keys) == set(data.keys())
#   result = OrderedDict({k: data[k] for k in sorted_keys})
#   return result


def sort_kld_parts(data: Dict[_T1, List[_T2]], target_dist: Dict[_T2, float], parts_count: int, take_per_part: int, lengths: OrderedDictType[_T1, Union[int, float]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> OrderedSet[_T1]:
  logger = getLogger(__name__)
  selection_mode = SelectionMode.FIRST
  result: OrderedSet[_T1] = OrderedSet()
  target_symbols_ordered: OrderedSet[_T2] = OrderedSet(sorted(target_dist.keys()))

  logger.info("Preparing data...")
  covered_counter = {x: 0 for x in target_symbols_ordered}
  target_dist_array = dict_to_array_ordered(target_dist, target_symbols_ordered)
  covered_array = dict_to_array_ordered(covered_counter, target_symbols_ordered)

  sorted_keys = get_keys_sort_after_value(lengths)
  parts_keys_ordered: List[OrderedSet[_T1]] = split_into_equal_parts(sorted_keys, parts_count)

  logger.info("Selecting data...")
  with tqdm(total=len(data)) as progress_bar:
    while len(result) != len(data):
      for part_keys_ordered in parts_keys_ordered:
        data_part = {k: data[k] for k in part_keys_ordered}
        available_entries_array = get_available_arrays(data_part, target_symbols_ordered)
        for _ in range(take_per_part):
          if len(available_entries_array) == 0:
            break
          potential_keys = get_utterance_with_min_kld(
            data=available_entries_array,
            covered_counts=covered_array,
            target_dist=target_dist_array,
            maxtasksperchild=maxtasksperchild,
            n_jobs=n_jobs,
            chunksize=chunksize,
          )

          if len(potential_keys) > 1:
            logger.info(f"Found {len(potential_keys)} candidates for the current iteration.")
          potential_keys_ordered = order_keys(potential_keys, part_keys_ordered)
          selected_key = select_key(potential_keys_ordered, unit_counts=None, mode=selection_mode)

          result.add(selected_key)
          covered_array += available_entries_array[selected_key]
          available_entries_array.pop(selected_key)
          part_keys_ordered.remove(selected_key)
          progress_bar.update()

  final_distr = __get_distribution(covered_array)
  final_kld = entropy(final_distr, target_dist_array)
  logger.info(f"Obtained Kullback-Leibler divergence: {final_kld}")

  return result


def sort_greedy_kld(data: OrderedDictType[_T1, List[_T2]], target_dist: Dict[_T2, float], n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> OrderedSet[_T1]:
  assert isinstance(data, OrderedDict)
  logger = getLogger(__name__)
  result: OrderedSet[_T1] = OrderedSet()
  # all_keys: Set[_T2] = set(target_dist.keys())
  # all_occuring_values: Set[_T2] = {x for y in data.values() for x in y}
  # assert all_keys == all_occuring_values
  target_symbols_ordered: OrderedSet[_T2] = OrderedSet(sorted(target_dist.keys()))
  # defines the order for what the selection is based on
  data_keys_ordered = OrderedSet(data.keys())

  logger.info("Preparing data...")
  covered_counter = {x: 0 for x in target_symbols_ordered}
  covered_array = dict_to_array_ordered(covered_counter, target_symbols_ordered)
  target_dist_array = dict_to_array_ordered(target_dist, target_symbols_ordered)
  available_entries_array = get_available_arrays(data, target_symbols_ordered)

  logger.info("Selecting data...")
  for _ in trange(len(available_entries_array)):
    potential_keys = get_utterance_with_min_kld(
      data=available_entries_array,
      covered_counts=covered_array,
      target_dist=target_dist_array,
      maxtasksperchild=maxtasksperchild,
      n_jobs=n_jobs,
      chunksize=chunksize,
    )
    potential_keys_ordered = order_keys(potential_keys, data_keys_ordered)
    selected_key = select_first(potential_keys_ordered)
    result.add(selected_key)
    covered_array += available_entries_array[selected_key]
    available_entries_array.pop(selected_key)
    data_keys_ordered.remove(selected_key)
  return result


def sort_greedy_kld_iterations(data: OrderedDictType[_T1, List[_T2]], target_dist: Dict[_T1, float], iterations: int, n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> OrderedSet[_T1]:
  assert isinstance(data, OrderedDict)
  logger = getLogger(__name__)
  result: OrderedSet[_T1] = OrderedSet()
  # must not be the case
  # all_keys = set(target_dist.keys())
  # all_occuring_values: Set[_T2] = {x for y in data.values() for x in y}
  # assert all_keys == all_occuring_values

  target_symbols_ordered: OrderedSet[_T2] = OrderedSet(sorted(target_dist.keys()))
  # defines the order for what the selection is based on
  data_keys_ordered = OrderedSet(data.keys())

  logger.info("Preparing data...")
  covered_counter = {x: 0 for x in target_symbols_ordered}
  covered_array = dict_to_array_ordered(covered_counter, target_symbols_ordered)
  target_dist_array = dict_to_array_ordered(target_dist, target_symbols_ordered)
  available_entries_array = get_available_arrays(data, target_symbols_ordered)

  logger.info("Selecting data...")
  its = min(iterations, len(available_entries_array))
  for _ in trange(its):
    potential_keys = get_utterance_with_min_kld(
      data=available_entries_array,
      covered_counts=covered_array,
      target_dist=target_dist_array,
      maxtasksperchild=maxtasksperchild,
      n_jobs=n_jobs,
      chunksize=chunksize,
    )
    potential_keys_ordered = order_keys(potential_keys, data_keys_ordered)
    selected_key = select_first(potential_keys_ordered)
    result.add(selected_key)
    covered_array += available_entries_array[selected_key]
    available_entries_array.pop(selected_key)
    data_keys_ordered.remove(selected_key)
  return result


def sort_greedy_kld_until(data: OrderedDictType[_T1, List[_T2]], target_dist: Dict[_T1, float], until_values: Dict[_T1, Union[float, int]], until_value: Union[float, int], n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> OrderedSet[_T1]:
  selection = sort_greedy_kld_until_with_preselection(
    data=data,
    target_dist=target_dist,
    until_values=until_values,
    until_value=until_value,
    preselection=OrderedDict(),
    chunksize=chunksize,
    maxtasksperchild=maxtasksperchild,
    n_jobs=n_jobs,
  )

  return selection


def sort_greedy_kld_until_with_preselection(data: OrderedDictType[_T1, List[_T2]], target_dist: Dict[_T2, float], until_values: Dict[_T1, Union[float, int]], until_value: Union[float, int], preselection: OrderedDictType[_T1, List[_T2]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> OrderedSet[_T1]:
  assert isinstance(data, OrderedDict)
  assert isinstance(preselection, OrderedDict)
  # The probability is really high that only one key is figured out, therefore it is useless to use any selection modes. If shortest or longest should be used the unfiltered count of symbols needs to be passed as extra parameter which increases complexity of the method.
  selection_mode = SelectionMode.FIRST
  logger = getLogger(__name__)
  result: OrderedSet[_T1] = OrderedSet()
  target_symbols_ordered: OrderedSet[_T2] = OrderedSet(sorted(target_dist.keys()))
  # defines the order for what the selection is based on
  data_keys_ordered = OrderedSet(data.keys())
  # all_occuring_values: Set[_T2] = {x for y in data.values() for x in y}
  # assert all_keys == all_occuring_values

  logger.info("Preparing data...")
  target_distribution_array = dict_to_array_ordered(target_dist, target_symbols_ordered)
  available_arrays = get_available_arrays(data, target_symbols_ordered)

  if len(preselection) == 0:
    covered_counter = {x: 0 for x in target_symbols_ordered}
    covered_array = dict_to_array_ordered(covered_counter, target_symbols_ordered)
  else:
    logger.info("Using preselected data.")
    preselection_array = get_available_arrays(preselection, target_symbols_ordered)
    covered_array = merge_arrays(preselection_array)
    preselection_distr = __get_distribution(covered_array)
    preselection_kld = entropy(preselection_distr, target_distribution_array)
    logger.info(f"Preselection Kullback-Leibler divergence: {preselection_kld}")

  all_occuring_ngrams_data: Set[_T2] = {x for y in data.values() for x in y}
  all_occuring_ngrams_preselection: Set[_T2] = {x for y in preselection.values() for x in y}
  all_occuring_ngrams: Set[_T2] = all_occuring_ngrams_data | all_occuring_ngrams_preselection
  missing_keys_in_data_and_preselection = target_symbols_ordered - all_occuring_ngrams
  if len(missing_keys_in_data_and_preselection) > 0:
    # is only relevant if the targed_distr for these keys is not zero.
    logger.warning(
      f"Some keys from targed distribution do not exist in data and preselection: {'.'.join(sorted(missing_keys_in_data_and_preselection))}")

  # if chunksize is None:
  #   chunksize = math.ceil(len(data) / n_jobs) / 2
  # logger.debug(f"Using {n_jobs} processes each handling chunks of {chunksize} for total data count {len(data)}.")

  logger.info("Selecting data...")
  max_until = sum(until_values.values())
  adjusted_until = round(min(until_value, max_until))
  current_total = 0.0
  with tqdm(total=adjusted_until, initial=round(current_total)) as progress_bar:
    while True:
      if len(available_arrays) == 0:
        logger.warning(
          f"Aborting selection as no further data is available! Selected: {current_total:.1f}/{until_value:.1f} ({current_total/until_value*100:.2f}%).")
        break
      potential_keys = get_utterance_with_min_kld(
        data=available_arrays,
        covered_counts=covered_array,
        target_dist=target_distribution_array,
        maxtasksperchild=maxtasksperchild,
        n_jobs=n_jobs,
        chunksize=chunksize,
      )
      if len(potential_keys) > 1:
        logger.info(f"Found {len(potential_keys)} candidates for the current iteration.")
      potential_keys_ordered = order_keys(potential_keys, data_keys_ordered)
      selected_key = select_key(potential_keys_ordered, unit_counts=None, mode=selection_mode)
      selected_until_value = until_values[selected_key]
      new_total = current_total + selected_until_value
      if new_total <= until_value:
        result.add(selected_key)
        covered_array += available_arrays[selected_key]
        current_total = new_total
        available_arrays.pop(selected_key)
        data_keys_ordered.remove(selected_key)
        progress_bar.update(round(selected_until_value))
        if current_total == until_value:
          break
      else:
        break

  final_distr = __get_distribution(covered_array)
  final_kld = entropy(final_distr, target_distribution_array)
  logger.info(f"Obtained Kullback-Leibler divergence: {final_kld}")

  return result


def get_utterance_with_min_kld(data: Dict[_T1, np.ndarray], covered_counts: np.ndarray, target_dist: np.ndarray, n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> Set[_T1]:
  divergences = get_divergences(data, covered_counts, target_dist,
                                n_jobs, maxtasksperchild, chunksize)
  all_with_minimum_divergence = get_smallest_divergence_keys(divergences)
  return all_with_minimum_divergence


process_data: Dict[_T1, np.ndarray] = None
process_covered_counts: np.ndarray = None
process_target_dist: np.ndarray = None


def init_pool(data: Dict[_T1, np.ndarray], covered_counts: np.ndarray, target_dist: np.ndarray) -> None:
  global process_data
  global process_covered_counts
  global process_target_dist
  process_data = data
  process_covered_counts = covered_counts
  process_target_dist = target_dist


def get_divergence_for_utterance(key: _T1) -> Tuple[_T1, float]:
  global process_data
  global process_covered_counts
  global process_target_dist
  utterance_counts = process_data[key]
  counts = process_covered_counts + utterance_counts
  distr = __get_distribution(counts)
  kld = get_kld(distr, process_target_dist)
  return key, kld


def get_divergences(data: Dict[_T1, np.ndarray], covered_counts: np.ndarray, target_dist: np.ndarray, n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> Dict[_T1, float]:
  # logger.debug(f"Using {thread_count} threads with {chunksize} chunks...")
  # logger.info("Calculating Kullback-Leibler divergences...")
  with Pool(
    processes=n_jobs,
    initializer=init_pool,
    initargs=(data, covered_counts, target_dist),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    result: Dict[_T1, float] = dict(pool.imap_unordered(
        get_divergence_for_utterance, data.keys(), chunksize=chunksize
    ))
  # logger.info("Done.")

  # res = process_map(meth, data.items(), max_workers=thread_count, chunksize=chunksize) # is equivalent but a bit slower
  # with ProcessPoolExecutor(max_workers=thread_count) as ex:
  #   #res = dict(tqdm(ex.map(meth, data.items(), chunksize=chunksize), total=len(data)))
  #   res = dict(ex.map(meth, data.items(), chunksize=chunksize))

  # todo: only return keys and then retrieve data
  # result: OrderedDictType[_T1, float] = OrderedDict({k: res[k] for k in data})

  return result


def get_smallest_divergence_keys(divergences: Dict[_T1, float]) -> Set[_T1]:
  assert len(divergences) > 0
  minimum_divergence = min(divergences.values())
  all_with_minimum_divergence = {
    key for key, divergence in divergences.items()
    if divergence == minimum_divergence
  }
  return all_with_minimum_divergence


def get_kld(dist: np.ndarray, target_dist: np.ndarray) -> float:
  none_of_targed_ngrams_exist = all(np.isnan(dist))
  if none_of_targed_ngrams_exist:
    return math.inf

  res = entropy(dist, target_dist)
  return res


def get_available_arrays(data: Dict[_T1, List[_T2]], target_symbols_ordered: OrderedSet[_T2]) -> Dict[_T1, np.ndarray]:
  available_entries_counter: Dict[_T1, Counter] = {
    k: Counter(v) for k, v in data.items()
  }

  for k in available_entries_counter:
    sync_dict_keys_to_keys_inplace(available_entries_counter[k], target_symbols_ordered)

  available_entries_arrays: Dict[_T1, np.ndarray] = {
    k: dict_to_array_ordered(counter, target_symbols_ordered)
    for k, counter in available_entries_counter.items()
  }

  return available_entries_arrays


def merge_arrays(data: Dict[_T1, np.ndarray]) -> np.ndarray:
  assert len(data) > 0
  merged_array = None
  for array in data.values():
    if merged_array is None:
      merged_array = array
    else:
      merged_array += array
  return merged_array


def __get_distribution(counts: np.ndarray) -> np.ndarray:
  # assert all(x >= 0 for x in counts) # too slow
  sum_counts = np.sum(counts)
  new_dist = np.divide(counts, sum_counts)
  return new_dist

# def _get_distribution(counts: np.ndarray) -> np.ndarray:
#   assert all(x >= 0 for x in counts)

#   sum_counts = np.sum(counts)

#   if sum_counts == 0:
#     return counts
#   else:
#     new_dist = np.divide(counts, sum_counts)
#     return new_dist


def get_uniform_distribution(ngrams: Dict[_T1, List[_T2]]) -> Dict[_T2, float]:
  unique_ngrams: Set[_T2] = {x for y in ngrams.values() for x in y}
  if len(unique_ngrams) == 0:
    return dict()
  distr = 1 / len(unique_ngrams)
  res: Dict[_T2, float] = {k: distr for k in unique_ngrams}
  return res


def sync_dict_keys_to_keys_inplace(dictionary: Dict[_T2, int], keys: Set[_T2]) -> None:
  """removes dictionary keys that are not in keys and addes keys that are in keys but not in dictionary with default value 0"""
  for k in keys:
    if k not in dictionary:
      dictionary[k] = 0
  keys_to_remove = set()
  for existing_key in dictionary:
    if existing_key not in keys:
      keys_to_remove.add(existing_key)
  for key_to_remove in keys_to_remove:
    dictionary.pop(key_to_remove)


def dict_to_array_ordered(d: Dict, order: OrderedSet) -> np.ndarray:
  assert isinstance(order, OrderedSet)
  assert set(d.keys()) == set(order)
  res = np.array([d[k] for k in sorted(d.keys())])
  return res
