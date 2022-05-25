from collections import OrderedDict
from typing import Dict, List, Optional
from typing import OrderedDict as OrderedDictType
from typing import Set

from ordered_set import OrderedSet

from text_selection.greedy.greedy_applied import (greedy_count, greedy_cover, greedy_default,
                                                  greedy_duration_advanced, greedy_epochs,
                                                  greedy_iterations, greedy_seconds)
from text_selection.selection import SelectionMode
from text_selection.utils import get_filtered_list, get_filtered_ngrams, get_top_n


def greedy_ngrams_cover(data: OrderedDictType[int, List[str]], already_covered: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], top_percent: Optional[float]) -> OrderedSet[int]:
  """
  cover each ngram at least one time
  top_percent: top percent of all data + already_covered occuring ngrams after filtering; 0 <= top_percent < 1
  """
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  already_covered_ngrams = get_filtered_ngrams(already_covered, n_gram, ignore_symbols)
  if top_percent is not None and 0 <= top_percent < 1:
    all_data = data_ngrams.copy()
    all_data.update(already_covered_ngrams)
    top_ngrams = get_top_n(all_data, top_percent)
    data_ngrams = OrderedDict([
      (k, get_filtered_list(v, top_ngrams))
      for k, v in data_ngrams.items()
    ])
    already_covered_ngrams = OrderedDict([
      (k, get_filtered_list(v, top_ngrams))
      for k, v in already_covered_ngrams.items()
    ])

  return greedy_cover(
    data=data_ngrams,
    already_covered=already_covered_ngrams,
  )


def greedy_ngrams_default(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]]) -> OrderedSet[int]:
  return greedy_default(
    data=get_filtered_ngrams(data, n_gram, ignore_symbols),
  )


def greedy_ngrams_seconds(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], durations_s: Dict[int, float], seconds: float) -> OrderedSet[int]:
  return greedy_seconds(
    data=get_filtered_ngrams(data, n_gram, ignore_symbols),
    durations_s=durations_s,
    seconds=seconds,
  )


def greedy_ngrams_durations_advanced(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], durations: Dict[int, float], target_duration: float, mode: SelectionMode) -> OrderedSet[int]:
  return greedy_duration_advanced(
    data=get_filtered_ngrams(data, n_gram, ignore_symbols),
    durations=durations,
    target_duration=target_duration,
    mode=mode,
  )


def greedy_ngrams_count(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], chars: Dict[int, int], total_count: int) -> OrderedSet[int]:
  return greedy_count(
    data=get_filtered_ngrams(data, n_gram, ignore_symbols),
    chars=chars,
    total_count=total_count,
  )


def greedy_ngrams_iterations(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], iterations: int) -> OrderedSet[int]:
  return greedy_iterations(
    data=get_filtered_ngrams(data, n_gram, ignore_symbols),
    iterations=iterations,
  )


def greedy_ngrams_epochs(data: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]], epochs: int) -> OrderedSet[int]:
  return greedy_epochs(
    data=get_filtered_ngrams(data, n_gram, ignore_symbols),
    epochs=epochs,
  )
