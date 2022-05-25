from collections import OrderedDict
from typing import Dict, List, Optional
from typing import OrderedDict as OrderedDictType
from typing import Set

from ordered_set import OrderedSet

from text_selection.greedy_kld_applied import (
    greedy_kld_uniform_count, greedy_kld_uniform_default,
    greedy_kld_uniform_iterations, greedy_kld_uniform_parts,
    greedy_kld_uniform_seconds, greedy_kld_uniform_seconds_with_preselection)
from text_selection.utils import (DurationBoundary, filter_data_durations,
                                  get_filtered_ngrams)


def greedy_kld_uniform_ngrams_parts(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], parts_count: int, take_per_part: int, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[int]:
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  lengths = OrderedDict([(k, len(v)) for k, v in data.items()])
  return greedy_kld_uniform_parts(
    data=data_ngrams,
    take_per_part=take_per_part,
    parts_count=parts_count,
    lengths=lengths,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )


def greedy_kld_uniform_ngrams_default(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[int]:
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  return greedy_kld_uniform_default(
    data=data_ngrams,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )


def greedy_kld_uniform_ngrams_iterations(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], iterations: int, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[int]:
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  return greedy_kld_uniform_iterations(
    data=data_ngrams,
    iterations=iterations,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )


def greedy_kld_uniform_ngrams_seconds(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], durations_s: Dict[int, float], seconds: float, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[int]:
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  return greedy_kld_uniform_seconds(
    data=data_ngrams,
    durations_s=durations_s,
    seconds=seconds,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )


def greedy_kld_uniform_ngrams_seconds_with_preselection(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], durations_s: Dict[int, float], seconds: float, preselection: OrderedDictType[int, List[str]], duration_boundary: DurationBoundary, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[int]:
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  data_ngrams = filter_data_durations(data_ngrams, durations_s, duration_boundary)
  preselection_ngrams = get_filtered_ngrams(preselection, n_gram, ignore_symbols)

  return greedy_kld_uniform_seconds_with_preselection(
    data=data_ngrams,
    durations_s=durations_s,
    seconds=seconds,
    preselection=preselection_ngrams,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )


def greedy_kld_uniform_ngrams_count(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], chars: Dict[int, int], total_count: int, n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int]) -> OrderedSet[int]:
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  return greedy_kld_uniform_count(
    data=data_ngrams,
    chars=chars,
    total_count=total_count,
    n_jobs=n_jobs,
    maxtasksperchild=maxtasksperchild,
    chunksize=chunksize,
  )

