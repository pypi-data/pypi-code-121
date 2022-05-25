import random
from collections import OrderedDict
from typing import OrderedDict as OrderedDictType
from typing import Set, TypeVar

from ordered_set import OrderedSet

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

def sort_random(data: OrderedDictType[_T1, _T2], seed: int) -> OrderedSet[_T1]:
  assert isinstance(data, OrderedDict)
  all_keys = list(data.keys())
  random.seed(seed)
  random.shuffle(all_keys)
  result: OrderedSet[_T1] = OrderedSet(all_keys)
  return result


def sort_random_set_cover(data: OrderedDictType[_T1, Set[_T2]], seed: int) -> OrderedSet[_T1]:
  """first select randomly to cover all occuring ngrams, then normal random"""
  assert isinstance(data, OrderedDict)
  all_ngrams = {x for y in data.values() for x in y}
  result: OrderedSet[_T1] = OrderedSet()
  random.seed(seed)
  covered = set()
  available = data.copy()
  while covered != all_ngrams:
    not_covered = all_ngrams - covered
    possible_keys = [
      k for k, val in available.items() if len(not_covered.intersection(val)) > 0
    ]
    choosen_key = random.choice(possible_keys)
    result.add(choosen_key)
    covered |= available[choosen_key]
    available.pop(choosen_key)
  all_remaining_keys = list(available.keys())
  random.shuffle(all_remaining_keys)
  remaining_random = OrderedSet(all_remaining_keys)
  result.update(remaining_random)
  return result
