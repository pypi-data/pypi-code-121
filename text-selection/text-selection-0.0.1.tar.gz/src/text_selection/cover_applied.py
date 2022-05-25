from typing import List
from typing import OrderedDict as OrderedDictType
from typing import Set, TypeVar

from ordered_set import OrderedSet
from text_selection.cover_methods import cover_default
from text_selection.utils import values_to_set

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def cover_symbols(data: OrderedDictType[_T1, List[_T2]], symbols: Set[_T2]) -> OrderedSet[_T1]:
  available_set = values_to_set(data)
  result = cover_default(data=available_set, to_cover=symbols)
  return result
