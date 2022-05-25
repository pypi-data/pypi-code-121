from collections import Counter
from logging import Logger
from typing import Any, Generator, Iterable, List, Optional
from typing import OrderedDict
from typing import OrderedDict as OrderedDictType
from typing import Tuple, Union

import numpy as np
from ordered_set import OrderedSet
from pandas import DataFrame

from text_selection_core.helper import split_adv
from text_selection_core.types import Dataset, DataWeights, Line, Lines, Subset, SubsetName
from text_selection_core.validation import (ValidationErr, ensure_lines_count_matches_dataset,
                                            ensure_weight_line_count_matches_dataset)

SPACE_DISPL = "␣"
NOT_AVAIL_VAL = "N/A"


def generate_statistics(dataset: Dataset, lines: Optional[Lines], ssep: str, weights: List[Tuple[str, DataWeights]], logger: Logger) -> Generator[Union[ValidationErr, Tuple[str, DataFrame]], None, None]:
  yield "Selection", get_selection_statistics(dataset)
  if len(weights) > 0:
    yield "Weights", get_weights_statistics(dataset, weights)
    for subset in get_subsets_ordered(dataset):
      yield f"Weights {subset}", get_subset_weights_statistics(dataset.subsets[subset], weights)
  if lines is not None:
    yield "Symbols", get_symbols_statistics(dataset, lines, ssep)


def get_subsets_ordered(dataset: Dataset) -> OrderedSet[str]:
  return OrderedSet(dataset.subsets.keys())


def get_all_symbols(lines: Iterable[Line], ssep: str) -> Generator[str, None, None]:
  result = (
    symbol
    for line in lines
    for symbol in split_adv(line, ssep)
  )
  return result


def get_symbols_statistics(dataset: Dataset, lines: Lines, ssep: str) -> Union[ValidationErr, DataFrame]:
  if error := ensure_lines_count_matches_dataset(dataset, lines):
    return error
  # TODO this as n_gram stats
  all_symbols = OrderedSet(sorted(set(get_all_symbols(lines, ssep))))

  subset_counts: OrderedDictType[SubsetName, Counter] = OrderedDict()
  subset_names = get_subsets_ordered(dataset)
  for subset_name in subset_names:
    subset = dataset.subsets[subset_name]
    subset_symbols_strs = (lines[data_id] for data_id in subset)
    #subset_symbols = set(get_all_symbols(subset_symbols_strs))
    #subset_matches = {symbol: "x" if symbol in subset_symbols else "-" for symbol in all_symbols}
    subset_matches = Counter(get_all_symbols(subset_symbols_strs, ssep))
    subset_counts[subset_name] = subset_matches
    # TODO add percent un-/covered as line

  #total_symbol_count = sum(sum(counters.values()) for counters in subset_contains_symbol.values())
  total_symbols_count = {
    symbol: sum(counters[symbol] for counters in subset_counts.values())
    for symbol in all_symbols
  }
  total_symbol_count = sum(total_symbols_count.values())

  result: List[OrderedDictType[str, Any]] = []
  for symbol in all_symbols:
    symbol_repr = repr(symbol)[1:-1] if symbol != " " else SPACE_DISPL
    row = {
      "Symbol": symbol_repr,
    }

    for subset, counts in subset_counts.items():
      row[f"Count {subset}"] = counts[symbol]
    symbol_count_total = sum(subset_counter[symbol] for subset_counter in subset_counts.values())
    row["Count Total"] = symbol_count_total

    for subset, counts in subset_counts.items():
      val = NOT_AVAIL_VAL if symbol_count_total == 0 else counts[symbol] / symbol_count_total * 100
      row[f"Count % {subset}"] = val

    for subset, counts in subset_counts.items():
      subset_total_count = sum(counts.values())
      val = NOT_AVAIL_VAL if subset_total_count == 0 else counts[symbol] / subset_total_count * 100
      row[f"Rel % {subset}"] = val

    val = NOT_AVAIL_VAL if total_symbol_count == 0 else symbol_count_total / total_symbol_count * 100
    row["Rel % Total"] = val
    result.append(row)

  if len(result) > 0:
    cols = result[0].keys()
    rows = (list(row.values()) for row in result)
    df = DataFrame(rows, columns=cols)
    return df
  return DataFrame()

  # for symbol in all_symbols:
  #   symbol_repr = repr(symbol)[1:-1] if symbol != " " else SPACE_DISPL
  #   counts = list(subset_counts[subset][symbol]
  #                 for subset in subset_counts)
  #   if total_symbol_count == 0:
  #     counts_percent_total = []
  #   else:
  #     counts_percent_total = list(count / total_symbol_count * 100 for count in counts)

  #   if symbol not in total_symbols_count or total_symbols_count[symbol] == 0:
  #     counts_percent_subset = []
  #   else:
  #     counts_percent_subset = list(count / total_symbols_count[symbol] * 100 for count in counts)

  #   line = [symbol_repr, total_symbols_count[symbol]] + \
  #       counts + counts_percent_total + counts_percent_subset
  #   data.append(line)
  # arr = np.array(data)

  # df = DataFrame(arr, columns=["Symbol", "Tot"] + list(subset_names) +
  #                list(subset_names) + list(subset_names))

  # return df


def get_selection_statistics(dataset: Dataset):
  data = []
  for subset_name in get_subsets_ordered(dataset):
    subset = dataset.subsets[subset_name]

    data.append((
      subset_name,
      len(subset),
      dataset.line_count - len(subset),
      dataset.line_count,
      len(subset) / dataset.line_count * 100,
      (dataset.line_count - len(subset)) / dataset.line_count * 100,
    ))

  df = DataFrame(
    data,
    columns=(
      "Name",
      "Sel",
      "Rst",
      "Tot",
      "Sel %",
      "Rst %",
    ),
  )

  return df


def get_subset_weights_statistics(subset: Subset, weights: List[Tuple[str, DataWeights]]):
  data = []
  for weights_name, data_weights in weights:
    data_weights_total = np.sum(data_weights)
    subset_weights = list(data_weights[k] for k in subset)
    weights_sum = sum(subset_weights)
    values = [weights_name]
    if len(subset_weights) == 0:
      values += [NOT_AVAIL_VAL] * 4
    else:
      values.extend((
        min(subset_weights),
        np.mean(subset_weights),
        np.median(subset_weights),
        max(subset_weights),
      ))
    values.extend((
      weights_sum,
      data_weights_total - weights_sum,
      data_weights_total,
    ))
    if data_weights_total == 0:
      values += [NOT_AVAIL_VAL] * 2
    else:
      values.extend((
        weights_sum / data_weights_total * 100,
        (data_weights_total - weights_sum) / data_weights_total * 100,
      ))
    data.append(values)

  df = DataFrame(data, columns=(
    "Name",
    "Min",
    "Avg",
    "Med",
    "Max",
    "Sum",
    "Rst",
    "Tot",
    "Sum %",
    "Rst %",
  ))

  return df


def get_weights_statistics(dataset: Dataset, weights: List[Tuple[str, DataWeights]]) -> Union[ValidationErr, DataFrame]:
  data = []
  for weights_name, data_weights in weights:
    if error := ensure_weight_line_count_matches_dataset(dataset, data_weights):
      return error
    data.append((
      weights_name,
      np.min(data_weights),
      np.mean(data_weights),
      np.median(data_weights),
      np.max(data_weights),
      np.sum(data_weights),
    ))

  df = DataFrame(
    data,
    columns=(
      "Name",
      "Min",
      "Avg",
      "Med",
      "Max",
      "Sum",
    ),
  )

  return df
