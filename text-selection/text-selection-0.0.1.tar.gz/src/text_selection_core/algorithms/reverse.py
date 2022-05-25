from typing import Iterator
from text_selection_core.types import LineNr, Subset


def get_reverse_iterator(subset: Subset) -> Iterator[LineNr]:
  ordered_subset = reversed(subset)
  return ordered_subset
