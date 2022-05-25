from typing import Iterator

from text_selection_core.types import LineNr, LineNrs, Subset


def get_fifo_subset_iterator(ids: LineNrs) -> Iterator[LineNr]:
  return iter(ids)


def get_line_nr_iterator(subset: Subset, ids: LineNrs) -> Iterator[LineNr]:
  ordered_subset = ids.intersection(subset)
  return iter(ordered_subset)

