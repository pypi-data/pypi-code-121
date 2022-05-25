from logging import getLogger
from typing import Iterator, Optional, Tuple, Union

import numpy as np
from ordered_set import OrderedSet
from scipy import special

from text_selection.selection import KeySelector


def get_uniform_weights(count: int) -> np.ndarray:
  result = np.ones(shape=(count), dtype=np.uint16)
  return result


def get_distributions_from_weights(weights: np.ndarray, data_len: int):
  target_dists = np.tile(weights, (data_len, 1))
  result = get_distribution(target_dists, axis=1)
  del target_dists
  return result


class KldIterator(Iterator[int]):
  def __init__(self, data: np.ndarray, data_indices: OrderedSet[int], weights: np.ndarray, preselection: np.ndarray, key_selector: KeySelector) -> None:
    super().__init__()
    assert len(weights) == 0 or np.sum(weights, axis=0) > 0
    self._data = data
    self._key_selector = key_selector
    # defines the order for what the selection is based on
    self.__available_data_keys_ordered = data_indices  # .copy()
    self.__covered_array = preselection.copy()
    self.__target_dists = get_distributions_from_weights(weights, len(data))
    self._previous_kld: Optional[float] = None
    self.__current_kld = get_kullback_leibler_divergence(
      pk=get_distribution(self.__covered_array, axis=0),
      qk=get_distribution(weights, axis=0),
      axis=0,
    )

  def __iter__(self) -> Iterator[int]:
    return self

  @property
  def previous_kld(self) -> Optional[float]:
    return self._previous_kld

  @property
  def current_kld(self) -> float:
    return self.__current_kld

  @property
  def target_distributions(self) -> float:
    return self.__target_dists

  def __next__(self) -> int:
    if len(self.__available_data_keys_ordered) == 0:
      raise StopIteration()

    min_div, potential_keys = get_minimum_kld_keys(
      data=self._data,
      keys=self.__available_data_keys_ordered,
      covered_counts=self.__covered_array,
      target_distributions=self.__target_dists,
    )

    if len(potential_keys) > 1:
      logger = getLogger(__name__)
      logger.info(f"Found {len(potential_keys)} candidates for the current iteration.")

    selected_key = self._key_selector.select_key(potential_keys)
    assert 0 <= selected_key < len(self._data)
    self.__covered_array += self._data[selected_key]
    self.__available_data_keys_ordered.remove(selected_key)
    self._previous_kld = self.__current_kld
    self.__current_kld = min_div

    return selected_key


def get_minimum_kld_keys(data: np.ndarray, keys: OrderedSet[int], covered_counts: np.ndarray, target_distributions: np.ndarray) -> Tuple[float, OrderedSet]:
  assert len(data.shape) == 2
  assert len(target_distributions.shape) == 2
  assert len(covered_counts.shape) == 1
  assert 0 < len(keys) <= len(data)
  data_subset: np.ndarray = data[keys]
  target_dist_subset: np.ndarray = target_distributions[keys]
  summed_counts = data_subset + covered_counts
  del data_subset
  min_div, indices = get_minimum_kld(summed_counts, target_dist_subset)
  del target_dist_subset
  mapped_indices = OrderedSet(keys[index] for index in indices)
  del indices
  return min_div, mapped_indices


def get_minimum_kld(counts: np.ndarray, target_distribution: np.ndarray) -> Tuple[float, np.ndarray]:
  assert len(counts) > 0
  assert len(counts.shape) == 2
  assert len(target_distribution.shape) == 2
  new_counts_distributions = get_distribution(counts, axis=1)
  divergences = get_kullback_leibler_divergence(
    new_counts_distributions, target_distribution, axis=1)
  del new_counts_distributions
  assert np.all(divergences >= 0.0)
  min_divergence, min_indices = get_minimum_indices(divergences)
  del divergences
  return min_divergence, min_indices


def get_minimum_indices(array: np.ndarray) -> Tuple[float, np.ndarray]:
  assert len(array) > 0
  min_value = array.min()
  min_indices = np.flatnonzero(array == min_value)
  return min_value, min_indices


def is_valid_distribution(qk: np.ndarray, axis: int) -> bool:
  """valid is e.g.: [], [1.0], [0.5, 0.5]"""
  """not valid is e.g.: [-1.0], [0.6, 0.6], [np.nan], [np.nan, 0.6], [1.2]"""
  assert 0 <= axis < len(qk.shape)
  if qk.shape[axis] == 0:
    return True
  if np.any(qk < 0.0):
    return False
  if np.any(qk > 1.0):
    return False

  #result = np.all(np.sum(qk, axis=axis) == 1)
  # TODO test
  result = np.all(np.isclose([np.sum(qk, axis=axis)], [1]))
  return result


def remove_nan_rows(pk: np.ndarray, axis: int) -> np.ndarray:
  """on axis=1: return empty only if all values are nan, otherwise keeps everything unchanged"""
  """on axis=2: removes all rows where all values are nan"""
  if pk.shape[axis] == 0:
    return pk

  indices = np.isnan(pk)
  indices = ~np.all(indices, axis=axis)
  if axis == 0:
    if indices == False:
      result = np.empty(shape=(0), dtype=pk.dtype)
      return result
    return pk
  result = pk[indices]
  return result


def get_kullback_leibler_divergence(pk: np.ndarray, qk: np.ndarray, axis: int) -> Union[float, np.ndarray]:
  """qk: target distribution"""
  assert pk.shape == qk.shape
  assert pk.dtype == qk.dtype
  assert 0 <= axis < len(pk.shape)
  assert is_valid_distribution(remove_nan_rows(pk, axis), axis)
  assert is_valid_distribution(qk, axis)
  # pylint: disable=no-member
  S = np.sum(special.rel_entr(pk, qk), axis=axis)
  # assignment is required for axis == 0 because single values can not be changed inplace
  S = np.nan_to_num(S, copy=False, nan=np.inf)
  return S


def is_valid_counts_or_weights(counts_or_weights: np.ndarray, axis: int) -> bool:
  assert 0 <= axis < len(counts_or_weights.shape)
  any_negative = np.any(counts_or_weights < 0, axis=axis)
  if np.any(any_negative, axis=0):
    return False
  indices = np.isnan(counts_or_weights)
  any_nan = np.any(indices, axis=axis)
  if np.any(any_nan, axis=0):
    return False
  return True


def get_distribution(counts_or_weights: np.ndarray, axis: int) -> np.ndarray:
  assert is_valid_counts_or_weights(counts_or_weights, axis)
  # new_dist = 1.0 * counts / np.sum(counts, axis=axis, keepdims=True)
  # new_dist: np.ndarray = np.array(counts / np.sum(counts, axis=axis, keepdims=True), dtype=np.float64)
  sum_counts = np.sum(counts_or_weights, axis=axis, dtype=np.float64, keepdims=True)
  new_dist = np.divide(counts_or_weights, sum_counts, dtype=np.float64)
  del sum_counts
  return new_dist
