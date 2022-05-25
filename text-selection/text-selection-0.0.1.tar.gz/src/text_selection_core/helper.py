
from typing import List, Optional

import numpy as np

from text_selection_core.types import DataWeights, Percent, Subset, Weight


def xtqdm(x, desc=None, unit=None, total=None):
  yield from x


# def merge_arrays(arrays: List[np.ndarray]) -> np.ndarray:
#   result = None
#   for array in arrays:
#     if result is None:
#       result = array
#     else:
#       result = np.append(result, array, axis=0)
#   return result

def get_chunks(keys: List[str], chunk_size: Optional[int]) -> List[List[str]]:
  if chunk_size is None:
    chunk_size = len(keys)
  chunked_list = list(keys[i: i + chunk_size] for i in range(0, len(keys), chunk_size))
  return chunked_list


dtype_order_uint = [
  np.uint8,
  np.uint16,
  np.uint32,
  np.uint64,
  # np.uint128,
  # np.uint256,
]

dtype_order_float = [
  np.float16,
  np.float32,
  np.float64,
]


def get_percent_str(current: int, total: int) -> str:
  if total == 0:
    return "N/A %"
  return f"{current /total*100:.2f}%"


def get_int_dtype_from_n(n: int) -> np.dtype:
  for dtype in dtype_order_uint:
    if n < np.iinfo(dtype).max:
      return dtype
  raise ValueError("Parameter 'n' to big for numpy!")


def get_float_dtype_from_n(n: float) -> np.dtype:
  for dtype in dtype_order_float:
    if n < np.finfo(dtype).max:
      return dtype
  raise ValueError("Parameter 'n' to big for numpy!")


def get_target_weights_from_percent(from_subset: Subset, to_subset: Subset, weights: DataWeights, target: Percent, target_incl_selection: bool) -> Weight:
  if target_incl_selection:
    target_value = target * sum(weights[k] for k in from_subset | to_subset) / 100
  else:
    target_value = target * sum(weights[k] for k in from_subset) / 100
  return target_value


def get_initial_weights(to_subset: Subset, weights: DataWeights, target_incl_selection: bool) -> Weight:
  if target_incl_selection:
    initial_weights = sum(weights[k] for k in to_subset)
  else:
    initial_weights = 0
  return initial_weights


def move_selection_between_subsets(from_subset: Subset, from_selection: Subset, to_subset: Subset) -> None:
  assert from_selection.issubset(from_subset)
  assert len(from_subset.intersection(to_subset)) == 0

  to_subset |= from_selection
  from_subset -= from_selection


def split_adv(s: str, sep: str) -> List[str]:
  if sep == "":
    return list(s)
  return s.split(sep)
