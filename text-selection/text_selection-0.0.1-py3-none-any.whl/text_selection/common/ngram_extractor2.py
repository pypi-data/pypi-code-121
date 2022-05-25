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
from text_selection.utils import log_mp_params
from text_utils import Symbol, Symbols
from tqdm import tqdm

NGramNr = int
NGramNrs = np.ndarray
NGram = Tuple[str, ...]


class NGramExtractor2():
  def __init__(self, n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> None:
    self.__fitted = False
    self.__n_jobs = n_jobs
    self.__maxtasksperchild = maxtasksperchild
    self.__chunksize = chunksize
    self.__n_gram: int = None
    self.__ngram_nr_to_ngram: OrderedDictType[NGram, NGramNr] = None
    self.__all_ngram_nrs: OrderedSet[NGramNr] = None
    self.__all_ngrams: OrderedSet[NGram] = None

  def fit(self, data: Iterable[Symbols], data_len: int, n_gram: int, ignore_symbols: Set[Symbol]) -> None:
    self.__n_gram = n_gram

    logger = getLogger(__name__)
    logger.debug(f"Collecting data symbols...")

    data_symbols = self.get_symbols(data, data_len)

    target_symbols = OrderedSet(sorted(data_symbols))
    target_symbols.difference_update(ignore_symbols)

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

  def predict(self, data: Iterable[Symbols], data_len: int) -> np.ndarray:
    assert self.__fitted

    result = np.zeros(shape=(data_len, len(self.__all_ngram_nrs)), dtype=np.uint16)
    if data_len == 0:
      return result

    logger = getLogger(__name__)
    logger.debug(f"Calculating {self.__n_gram}-grams...")

    log_mp_params(self.__n_jobs, self.__chunksize, self.__maxtasksperchild, data_len)

    method_proxy = partial(
      get_ngram_counts_from_data_entry,
      n=self.__n_gram,
    )

    with Pool(
        processes=self.__n_jobs,
        initializer=get_ngrams_counts_from_data_init_pool,
        initargs=(self.__ngram_nr_to_ngram, self.__all_ngram_nrs),
        maxtasksperchild=self.__maxtasksperchild,
      ) as pool:

      iterator = pool.imap_unordered(method_proxy, enumerate(data), chunksize=self.__chunksize)
      with tqdm(total=data_len, desc="N-gram prediction") as pbar:
        for index, counts in iterator:
          result[index] = counts
          pbar.update()

    return result

  def get_symbols(self, data: Iterable[Symbols], data_len: int) -> Set[Symbol]:
    result = set()
    if data_len == 0:
      return result

    logger = getLogger(__name__)
    logger.debug(f"Calculating symbol...")

    log_mp_params(self.__n_jobs, self.__chunksize, self.__maxtasksperchild, data_len)

    with Pool(
        processes=self.__n_jobs,
        maxtasksperchild=self.__maxtasksperchild,
      ) as pool:
      iterator = pool.imap_unordered(get_symbols_from_item, data, chunksize=self.__chunksize)
      with tqdm(total=data_len, desc="Symbol detection") as pbar:
        for unique_symbols in iterator:
          result.update(unique_symbols)
          pbar.update()

    return result


def get_symbols_from_item(item: Symbols) -> Set[Symbol]:
  result = set(item)
  return result


def get_all_ngrams_iterator(symbols: OrderedSet[str], n_gram: int) -> Iterator[NGram]:
  possible_ngrams = itertools.product(symbols, repeat=n_gram)
  return possible_ngrams


def generate_numerated_ngrams(ngrams: Iterable[NGram]) -> Generator[Tuple[NGram, int], None, None]:
  numerated_ngrams = ((k, i) for i, k in enumerate(ngrams))
  return numerated_ngrams


process_ngram_nr_to_ngram: Dict[NGram, NGramNr] = None
process_ngram_nrs: OrderedSet[NGramNr] = None


def get_ngrams_counts_from_data_init_pool(ngram_nr_to_ngram: Dict[NGram, NGramNr], ngram_nrs: OrderedSet[NGramNr]) -> None:
  global process_ngram_nr_to_ngram
  global process_ngram_nrs
  process_ngram_nr_to_ngram = ngram_nr_to_ngram
  process_ngram_nrs = ngram_nrs


def get_ngram_counts_from_data_entry(index_symbols: Tuple[int, Symbols], n: int) -> Tuple[int, np.ndarray]:
  # pylint: disable=global-variable-not-assigned
  global process_ngram_nr_to_ngram
  global process_ngram_nrs
  index, symbols = index_symbols

  result = get_ngram_counts_from_data_entry_core(
    n, symbols, process_ngram_nr_to_ngram, process_ngram_nrs)

  del symbols

  return index, result


def get_ngram_counts_from_data_entry_core(n: int, symbols: Symbols, ngram_nr_to_ngram: Dict[NGram, NGramNr], all_ngram_nrs: OrderedSet[NGramNr]) -> np.ndarray:
  ngram_nrs = (
    ngram_nr_to_ngram[ngram]
    for ngram in get_ngrams_generator(symbols, n)
    if ngram in ngram_nr_to_ngram
  )

  result = get_count_array(ngram_nrs, all_ngram_nrs)
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


def get_ngrams_generator(sentence_symbols: Symbols, n: int) -> Generator[NGram, None, None]:
  assert n > 0
  result = (
    tuple(sentence_symbols[i:i + n])
    for i in range(len(sentence_symbols) - n + 1)
  )
  return result
