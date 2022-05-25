import math
from collections import OrderedDict
from typing import Dict, List
from typing import OrderedDict as OrderedDictType
from typing import TypeVar

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def get_rarity_item(item: _T2, distribution: Dict[_T2, float]) -> float:
  if item in distribution:
    return distribution[item]
  return 0


def get_rarity_list(utterance: List[_T2], distribution: Dict[_T2, float]) -> float:
  if len(utterance) == 0:
    return math.inf
  dists = [get_rarity_item(x, distribution) for x in utterance]
  dist_avg = sum(dists) / len(utterance)
  return dist_avg


def get_rarity_data(data: OrderedDictType[_T1, List[_T2]], distribution: Dict[_T2, float]) -> OrderedDictType[_T1, float]:
  res = OrderedDict([(k, get_rarity_list(v, distribution)) for k, v in data.items()])
  return res
