from typing import List
from typing import OrderedDict as OrderedDictType
from typing import Set

from ordered_set import OrderedSet

from text_selection.cover_applied import cover_symbols


def cover_symbols_default(data: OrderedDictType[int, List[str]], symbols: Set[str]) -> OrderedSet[int]:
  return cover_symbols(
    data=data,
    symbols=symbols,
  )
