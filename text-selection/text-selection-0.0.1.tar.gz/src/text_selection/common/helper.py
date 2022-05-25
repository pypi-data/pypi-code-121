from typing import Dict, Optional, Set, Tuple

import numpy as np
from numpy import ndarray
from ordered_set import OrderedSet
from text_selection.common.ngram_extractor import NGramExtractor


def get_ngram_counts(data: Dict[int, Tuple[str, ...]], select_from_keys: OrderedSet[int], preselection_keys: Set[int], n_gram: int, ignore_symbols: Optional[Set[str]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int], batches: Optional[int]) -> Tuple[np.ndarray, np.ndarray]:
  ngram_extractor = NGramExtractor(data, n_jobs, maxtasksperchild, chunksize, batches)
  ngram_extractor.fit(select_from_keys | preselection_keys, n_gram, ignore_symbols)
  all_data_counts = ngram_extractor.predict(select_from_keys)
  all_preselected_counts = ngram_extractor.predict(preselection_keys)
  del ngram_extractor
  summed_preselection_counts: np.ndarray = np.sum(all_preselected_counts, axis=0)
  del all_preselected_counts
  return all_data_counts, summed_preselection_counts


def get_empty_columns(data: ndarray, data_indices: Set[int], preselection: ndarray) -> ndarray:
  """ remove empty columns, can only occur on ngram=1 if len(symbols in utterance) = n_gram - 1 and otherwise if two or threegrams do not exist"""
  assert len(data.shape) == 2
  assert len(preselection.shape) == 1
  assert data.shape[1] == preselection.shape[0]

  if len(data_indices) == 0:
    data_counts = np.zeros_like(preselection)
  else:
    data_counts: ndarray = np.sum(data[list(data_indices)], axis=0)
  all_counts: ndarray = data_counts + preselection
  del data_counts
  remove_ngram_indices = np.where(all_counts == 0)[0]
  del all_counts

  return remove_ngram_indices
