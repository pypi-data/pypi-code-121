from collections import Counter
from functools import partial
from itertools import chain
from logging import Logger
from multiprocessing import Pool
from typing import List, Optional, Tuple

import numpy as np
from ordered_set import OrderedSet
from tqdm import tqdm
from text_selection_core.globals import TQDM_LINE_UNIT

from text_selection_core.helper import get_chunks, get_int_dtype_from_n, split_adv, xtqdm
from text_selection_core.types import Lines, Subset

SymbolCounts = np.ndarray
ColumnSymbols = OrderedSet[str]


# def get_symbols_from_lines(lines: Lines, subset: Subset, ssep: str) -> Set[str]:
#   symbols = {
#     symbol
#     for line_nr in tqdm(subset, desc="Getting unique symbols", unit=TQDM_LINE_UNIT)
#     for symbol in split_adv(lines[line_nr], ssep)
#   }
#   return symbols


# def get_array(lines: Lines, subset: Subset, ssep: str, logger: Logger):
#   start = perf_counter()
#   # 1mio -> 8.4
#   # 10mio -> 84.94535316200927s
#   # get_array_v1(lines, subset, ssep, logger)
#   # 1mio -> 10.079393691034056s
#   # 10mio -> 92.748770733946s
#   # get_array_v2(lines, subset, ssep, logger)  # 10.079393691034056s
#   result = get_array_mp(lines, subset, ssep, logger, 1_000_000, 16, None)
#   duration = perf_counter() - start
#   logger = getLogger()
#   logger.info(f"Duration: {duration}s")
#   return result


def get_array_mp(lines: Lines, subset: Subset, ssep: str, logger: Logger, chunksize: int, n_jobs: int, maxtasksperchild: Optional[int]) -> Tuple[SymbolCounts, ColumnSymbols]:
  subset_chunks = get_chunks(subset, chunksize)
  method = partial(
    process_get_array,
    ssep=ssep,
  )

  logger.debug(f"# Lines: {len(lines)}")
  logger.debug(f"# Subset lines: {len(subset)}")
  logger.debug(f"Chunksize: {chunksize}")
  logger.debug(f"Chunks: {len(subset_chunks)}")
  logger.debug(f"Maxtask: {maxtasksperchild}")
  logger.debug(f"Jobs: {n_jobs}")

  n_jobs = min(n_jobs, len(subset_chunks))
  logger.debug(f"Jobs (final): {n_jobs}")

  with Pool(
    processes=n_jobs,
    maxtasksperchild=maxtasksperchild,
    initializer=init_mp,
    initargs=(lines,),
  ) as pool:
    arrays = dict(tqdm(pool.imap_unordered(
        method, enumerate(subset_chunks), chunksize=1
    ), total=len(subset_chunks), desc="Processing chunks"))
  arrays = sorted(arrays.items(), key=lambda kv: kv[0])
  arrays = list(v for k, v in arrays)
  arrays, symbols = unify_arrays(arrays)
  with tqdm(total=len(arrays), desc="Merging chunks") as pbar:
    array = arrays.pop(0)
    pbar.update()
    while len(arrays) > 0:
      current = arrays.pop(0)
      array = np.append(array, current, axis=0)
      del current
      pbar.update()

  return array, symbols


def init_mp(lines: Lines) -> None:
  global process_lines
  process_lines = lines


def process_get_array(i_subset: Tuple[int, Subset], ssep: str) -> Tuple[int, Tuple[SymbolCounts, ColumnSymbols]]:
  global process_lines
  i, subset = i_subset
  result = get_array(process_lines, subset, ssep)
  return i, result


def unify_arrays(arrays_symbols: List[Tuple[SymbolCounts, ColumnSymbols]]) -> Tuple[List[SymbolCounts], ColumnSymbols]:
  all_symbols = OrderedSet({
    symbol
    for _, symbols in arrays_symbols
    for symbol in symbols
  })

  array: SymbolCounts
  symbols: ColumnSymbols
  for i, (array, symbols) in enumerate(tqdm(arrays_symbols, desc="Unifying chunks")):
    missing_symbols = all_symbols - symbols
    if len(missing_symbols) > 0:
      new_cols = np.zeros((len(array), len(missing_symbols)), dtype=array.dtype)
      array = np.append(array, new_cols, axis=1)
      symbols.update(missing_symbols)

    assert len(symbols) == len(all_symbols)
    symbols_mapping = [
      symbols.index(s)
      for s in all_symbols
    ]

    array = array[:, symbols_mapping]
    arrays_symbols[i] = array

  return arrays_symbols, all_symbols


def get_array(lines: Lines, subset: Subset, ssep: str) -> Tuple[SymbolCounts, ColumnSymbols]:
  counters: List[Counter] = []
  for line_nr in xtqdm(subset, desc="Calculating counts", unit=TQDM_LINE_UNIT):
    line_counts = Counter(split_adv(lines[line_nr], ssep))
    counters.append(line_counts)

  symbols = OrderedSet(set(chain(*counters)))
  max_count = max(max(counter.values()) for counter in counters)

  dtype = get_int_dtype_from_n(max_count)
  # logger.debug(f"Chosen dtype \"{dtype}\" for numpy because maximum count is {max_count}.")

  # symbols.difference_update(ignore)
  symbols_indices = dict((s, i) for i, s in enumerate(symbols))

  result = np.zeros((len(counters), len(symbols)), dtype=dtype)

  for line_index, counter in enumerate(xtqdm(counters)):
    for symbol, count in counter.items():
      # if symbol in symbols_indices:
      symbol_index = symbols_indices[symbol]
      result[line_index, symbol_index] = count
  del counters
  del symbols_indices
  del max_count
  return result, symbols

# def get_array_v2(lines: Lines, subset: Subset, ssep: str, logger: Logger):
#   result = None
#   symbols_indicies = {}

#   for line_nr in tqdm(subset, desc="Calculating counts", unit=TQDM_LINE_UNIT):
#     line_counts = Counter(lines[line_nr].split(ssep))
#     if result is None:
#       result = np.zeros((len(subset), len(line_counts)), dtype=np.uint16)
#       symbols_indicies = dict((s, i) for i, s in enumerate(line_counts))
#     else:
#       new_symbols = line_counts.keys() - symbols_indicies.keys()
#       # new_symbols = set(line_counts.keys()).difference(symbols_indicies.keys())
#       if len(new_symbols) > 0:
#         new_col = np.zeros((len(subset), len(new_symbols)), dtype=np.uint16)
#         result = np.append(result, new_col, axis=1)
#         for new_symbol in new_symbols:
#           symbols_indicies[new_symbol] = len(symbols_indicies)

#     for symbol, count in line_counts.items():
#       symbol_index = symbols_indicies[symbol]
#       result[line_nr, symbol_index] = count
#   return result, symbols_indicies
