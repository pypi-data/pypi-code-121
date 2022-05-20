""" Prototype Code """
from dataclasses import dataclass

from typing import TypeVar, Iterable, Callable, List, Dict, Any

T = TypeVar('T')
X = TypeVar('X')
Y = TypeVar('Y')
Z = TypeVar('Z')


class SimpleStream:
    def __init__(self, source: Iterable[T]):
        self._source = source
        self._operations: List[Operation] = []

    def filter(self, executable: Callable[[X], bool]):
        self._operations.append(Operation(op='filter', executable=executable))
        return self

    def map(self, executable: Callable[[X], Y]):
        self._operations.append(Operation(op='map', executable=executable))
        return self

    def run(self):
        for __ in self._run():
            pass  # This is basically just to run the whole stream without caring about the result.

    def to_list(self) -> List[Any]:
        return [item for item in self._run()]

    def to_map(self, key_mapper: Callable[[X], Y], value_mapper: Callable[[X], Z]) -> Dict[Y, Z]:
        result: Dict[Y, Z] = dict()

        for item in self._run():
            result[key_mapper(item)] = value_mapper(item)

        return result

    def find_first(self) -> Any:
        for item in self._run():
            return item
        return None

    def any_matched(self) -> bool:
        return self.find_first() is not None

    def for_each(self, executable: Callable[[X], None]):
        for item in self._run():
            executable(item)

    def _run(self):
        for item in self._source:
            included = True
            result = item

            for operation in self._operations:
                if not included:
                    continue

                if operation.op == 'filter':
                    included = operation.executable(item)

                if operation.op == 'map':
                    result = operation.executable(result)

            if included:
                yield result


@dataclass(frozen=True)
class Operation:
    op: str
    executable: Callable
