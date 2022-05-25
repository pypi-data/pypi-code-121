import math
from logging import getLogger
from typing import Dict, List, Optional, OrderedDict, TypeVar, Union

from ordered_set import OrderedSet

from text_selection.greedy_kld_methods import (
    get_uniform_distribution, sort_greedy_kld, sort_greedy_kld_iterations,
    sort_greedy_kld_until, sort_greedy_kld_until_with_preselection,
    sort_kld_parts)

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def greedy_kld_uniform_parts(data: Dict[_T1, List[_T2]], parts_count: int, take_per_part: int, lengths: OrderedDict[_T1, Union[int, float]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[_T1]:
  uniform_distr = get_uniform_distribution(data)
  if chunksize is None:
    chunksize = get_chunksize_for_data(data, n_jobs)
  greedy_selected = sort_kld_parts(
    data=data,
    target_dist=uniform_distr,
    parts_count=parts_count,
    take_per_part=take_per_part,
    lengths=lengths,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )
  return greedy_selected


def greedy_kld_uniform_default(data: OrderedDict[_T1, List[_T2]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[_T1]:
  uniform_distr = get_uniform_distribution(data)
  if chunksize is None:
    chunksize = get_chunksize_for_data(data, n_jobs)
  greedy_selected = sort_greedy_kld(
    data=data,
    target_dist=uniform_distr,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )
  return greedy_selected


def greedy_kld_uniform_iterations(data: OrderedDict[_T1, List[_T2]], iterations: int, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[_T1]:
  uniform_distr = get_uniform_distribution(data)
  if chunksize is None:
    chunksize = get_chunksize_for_data(data, n_jobs)
  greedy_selected = sort_greedy_kld_iterations(
    data=data,
    target_dist=uniform_distr,
    iterations=iterations,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )
  return greedy_selected


def greedy_kld_uniform_seconds(data: OrderedDict[_T1, List[_T2]], durations_s: Dict[int, float], seconds: float, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[_T1]:
  logger = getLogger(__name__)
  uniform_distr = get_uniform_distribution(data)
  if len(uniform_distr) > 0:
    logger.info(f"Target uniform distribution: {list(uniform_distr.values())[0]}")
  if chunksize is None:
    chunksize = get_chunksize_for_data(data, n_jobs)
  greedy_selected = sort_greedy_kld_until(
    data=data,
    target_dist=uniform_distr,
    until_values=durations_s,
    until_value=seconds,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )
  return greedy_selected


def get_chunksize_for_data(data: OrderedDict, n_jobs: int) -> int:
  if len(data) == 0:
    return 1
  chunksize = math.ceil(len(data) / n_jobs)
  return chunksize


def greedy_kld_uniform_seconds_with_preselection(data: OrderedDict[_T1, List[_T2]], durations_s: Dict[int, float], seconds: float, preselection: OrderedDict[_T1, List[_T2]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[_T1]:
  logger = getLogger(__name__)
  uniform_distr = get_uniform_distribution(data)
  if len(uniform_distr) > 0:
    logger.info(f"Target uniform distribution: {list(uniform_distr.values())[0]}")
  if chunksize is None:
    chunksize = get_chunksize_for_data(data, n_jobs)
  greedy_selected = sort_greedy_kld_until_with_preselection(
    data=data,
    target_dist=uniform_distr,
    until_values=durations_s,
    until_value=seconds,
    preselection=preselection,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )

  return greedy_selected


def greedy_kld_uniform_count(data: OrderedDict[_T1, List[_T2]], chars: Dict[int, int], total_count: int, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[_T1]:
  uniform_distr = get_uniform_distribution(data)
  if chunksize is None:
    chunksize = get_chunksize_for_data(data, n_jobs)
  greedy_selected = sort_greedy_kld_until(
    data=data,
    target_dist=uniform_distr,
    until_values=chars,
    until_value=total_count,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )
  return greedy_selected
