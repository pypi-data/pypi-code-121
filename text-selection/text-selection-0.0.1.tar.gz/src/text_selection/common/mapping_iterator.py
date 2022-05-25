from typing import Dict, Generator, Iterable, Iterator


class MappingIterator(Iterator[int]):
  def __init__(self, iterator: Iterator[int], mapping: Dict[int, int]) -> None:
    super().__init__()
    self.iterator = iterator
    self.mapping = mapping

  def __iter__(self) -> Iterator[int]:
    return self

  def __next__(self) -> int:
    result = next(self.iterator)
    assert result in self.mapping
    mapped_result = self.mapping[result]
    return mapped_result


def map_indices(iterator: Iterable[int], mapping: Dict[int, int]) -> Generator[int, None, None]:
  for key in iterator:
    assert key in mapping
    mapped_key = mapping[key]
    yield mapped_key
