import itertools
from collections import Counter, OrderedDict
from functools import partial
from logging import getLogger
from multiprocessing import Pool
from typing import Dict, Generator, Iterable, Iterator, Optional
from typing import OrderedDict as OrderedDictType
from typing import Set, Tuple

import numpy as np
from ordered_set import OrderedSet
from text_selection.utils import get_chunksize, log_mp_params
from tqdm import tqdm

NGramNr = int
NGramNrs = np.ndarray
NGram = Tuple[str, ...]


class NGramExtractor():
  def __init__(self, data: Dict[int, Tuple[str, ...]], n_jobs: int, maxtasksperchild: Optional[int], chunksize: Optional[int], batches: Optional[int]) -> None:
    self.__data = data
    self.__fitted = False
    self.__n_jobs = n_jobs
    self.__maxtasksperchild = maxtasksperchild
    self.__chunksize = chunksize
    self.__batches = batches
    self.__consider_keys: Set[int] = None
    self.__n_gram: int = None
    self.__ngram_nr_to_ngram: OrderedDictType[NGram, NGramNr] = None
    self.__all_ngram_nrs: OrderedSet[NGramNr] = None
    self.__all_ngrams: OrderedSet[NGram] = None

  def fit(self, consider_keys: Set[int], n_gram: int, ignore_symbols: Optional[Set[str]]) -> None:
    consider_keys_exist_in_data = consider_keys.issubset(self.__data.keys())
    assert consider_keys_exist_in_data

    self.__consider_keys = consider_keys
    self.__n_gram = n_gram

    logger = getLogger(__name__)
    logger.debug(f"Collecting data symbols...")
    data_symbols = get_unique_symbols(self.__data, consider_keys)
    target_symbols = OrderedSet(sorted(data_symbols))
    if ignore_symbols is not None:
      target_symbols -= ignore_symbols

    logger.debug(f"Calculating all possible {n_gram}-grams...")
    possible_ngrams = get_all_ngrams_iterator(target_symbols, n_gram)
    nummerated_ngrams = generate_numerated_ngrams(possible_ngrams)
    self.__ngram_nr_to_ngram: OrderedDictType[NGram, NGramNr] = OrderedDict(nummerated_ngrams)
    self.__all_ngram_nrs: OrderedSet[NGramNr] = OrderedSet(self.__ngram_nr_to_ngram.values())
    self.__all_ngrams: OrderedSet[NGram] = OrderedSet(self.__ngram_nr_to_ngram.keys())

    log_top_n = 100
    ngrams_str = sorted((
      f"{''.join(n_gram).replace(' ', '␣')}" for n_gram in self.__all_ngrams[:log_top_n]
    ))
    logger.debug(
      f"Obtained {len(self.__all_ngrams)} different {self.__n_gram}-gram(s): {' '.join(ngrams_str)} ...")
    self.__fitted = True

  @property
  def ngram_nr_to_ngram(self) -> OrderedDictType[NGram, NGramNr]:
    assert self.__fitted
    return self.__ngram_nr_to_ngram

  @property
  def fitted_ngrams(self) -> OrderedSet[NGram]:
    assert self.__fitted
    return self.__all_ngrams

  def predict(self, keys: OrderedSet[int]) -> np.ndarray:
    assert isinstance(keys, OrderedSet)
    assert self.__fitted
    keys_are_subset_of_fitted_keys = keys.issubset(self.__consider_keys)
    assert keys_are_subset_of_fitted_keys

    result = np.zeros(shape=(len(keys), len(self.__all_ngram_nrs)), dtype=np.uint16)
    if len(keys) == 0:
      return result

    logger = getLogger(__name__)
    logger.debug(f"Calculating {self.__n_gram}-grams...")

    final_chunksize = get_chunksize(len(keys), self.__n_jobs, self.__chunksize, self.__batches)
    log_mp_params(self.__n_jobs, final_chunksize, self.__maxtasksperchild, len(keys))

    method_proxy = partial(
      get_ngram_counts_from_data_entry,
      n=self.__n_gram,
    )

    with Pool(
        processes=self.__n_jobs,
        initializer=get_ngrams_counts_from_data_init_pool,
        initargs=(self.__data, self.__ngram_nr_to_ngram, self.__all_ngram_nrs),
        maxtasksperchild=self.__maxtasksperchild,
      ) as pool:
      with tqdm(total=len(keys), desc="N-gram prediction") as pbar:
        iterator = pool.imap_unordered(method_proxy, enumerate(keys), chunksize=final_chunksize)
        for index, counts in iterator:
          result[index] = counts
          pbar.update()

    return result


def get_unique_symbols(data: Dict[int, Tuple[str, ...]], keys: Set[int]) -> Set[str]:
  occurring_symbols = {symbol for key in tqdm(keys, total=len(keys)) for symbol in data[key]}
  return occurring_symbols


def get_all_ngrams_iterator(symbols: OrderedSet[str], n_gram: int) -> Iterator[NGram]:
  possible_ngrams = itertools.product(symbols, repeat=n_gram)
  return possible_ngrams


def generate_numerated_ngrams(ngrams: Iterable[NGram]) -> Generator[Tuple[NGram, int], None, None]:
  numerated_ngrams = ((k, i) for i, k in enumerate(ngrams))
  return numerated_ngrams


process_ngram_nr_to_ngram: Dict[NGram, NGramNr] = None
process_data: OrderedDictType[int, Tuple[str, ...]] = None
process_ngram_nrs: OrderedSet[NGramNr] = None


def get_ngrams_counts_from_data_init_pool(data: OrderedDictType[int, Tuple[str, ...]], ngram_nr_to_ngram: Dict[NGram, NGramNr], ngram_nrs: OrderedSet[NGramNr]) -> None:
  global process_data
  global process_ngram_nr_to_ngram
  global process_ngram_nrs
  process_data = data
  process_ngram_nr_to_ngram = ngram_nr_to_ngram
  process_ngram_nrs = ngram_nrs


def get_ngram_counts_from_data_entry(index_key: Tuple[int, int], n: int) -> Tuple[int, np.ndarray]:
  # pylint: disable=global-variable-not-assigned
  global process_data
  global process_ngram_nr_to_ngram
  global process_ngram_nrs
  index, key = index_key

  result = get_ngram_counts_from_data_entry_core(
    key=key,
    n=n,
    data=process_data,
    ngram_nr_to_ngram=process_ngram_nr_to_ngram,
    all_ngram_nrs=process_ngram_nrs,
  )

  del key

  return index, result


def get_ngram_counts_from_data_entry_core(key: int, n: int, data: OrderedDictType[int, Tuple[str, ...]], ngram_nr_to_ngram: Dict[NGram, NGramNr], all_ngram_nrs: OrderedSet[NGramNr]) -> np.ndarray:
  assert key in data
  symbols = data[key]

  ngram_nrs = (
    ngram_nr_to_ngram[ngram]
    for ngram in get_ngrams_generator(symbols, n)
    if ngram in ngram_nr_to_ngram
  )

  result = get_count_array(ngram_nrs, all_ngram_nrs)
  del symbols
  del ngram_nrs

  return result


def get_count_array(ngram_nrs: Iterable[NGramNr], target_symbols_ordered: OrderedSet[NGramNr]) -> np.ndarray:
  ngram_nr_counts = Counter(ngram_nrs)
  res_tuple = tuple(
    ngram_nr_counts.get(ngram_nr, 0)
    for ngram_nr in target_symbols_ordered
  )
  del ngram_nr_counts

  result = np.array(res_tuple, dtype=np.uint16)
  del res_tuple

  return result


def get_ngrams_generator(sentence_symbols: Tuple[str, ...], n: int) -> Generator[NGram, None, None]:
  assert n > 0
  result = (
    tuple(sentence_symbols[i:i + n])
    for i in range(len(sentence_symbols) - n + 1)
  )
  return result
