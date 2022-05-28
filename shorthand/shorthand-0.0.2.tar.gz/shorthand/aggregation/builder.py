from typing import Callable, Any

from shorthand.aggregation.aggregation import Aggregation


_EMPTY = type("_EMPTY", (), {})()


class AggregationBuilder:
    def __init__(self, key: Any = _EMPTY):
        self._key = key

    def add(self) -> Aggregation:
        return self._build(lambda current, new: current + new)

    def mul(self) -> Aggregation:
        return self._build(lambda current, new: current * new)

    def new(self) -> Aggregation:
        return self._build(lambda current, new: new)

    def current(self) -> Aggregation:
        return self._build(lambda current, new: current)

    def append(self) -> Aggregation:
        def _f(current: Any, new: Any) -> Any:
            current.append(new)
            return current
        return self._build(_f)

    def unique(self) -> Aggregation:
        def _f(current: Any, new: Any) -> Any:
            current.add(new)
            return current
        return self._build(_f)

    def __getitem__(self, key: Any) -> 'AggregationBuilder':
        return AggregationBuilder(key)

    def _build(self, f: Callable[[Any, Any], Any]) -> Aggregation:
        if self._key is _EMPTY:
            return Aggregation(f)

        def _f(current: Any, new: Any) -> Any:
            current[self._key] = f(current[self._key], new)
            return current

        return Aggregation(_f)


A: AggregationBuilder = AggregationBuilder()
