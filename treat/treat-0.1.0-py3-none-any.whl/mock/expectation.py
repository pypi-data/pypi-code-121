import inspect

from enum import Enum
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from treat.mock.exceptions import InvalidMockCallsCount


_UNSET = object()


class ExpectationKind(Enum):

    METHOD = "method"
    PROPERTY = "property"
    ATTRIBUTE = "attribute"


class Expectation:
    def __init__(
        self,
        name: str,
        kind: ExpectationKind,
    ) -> None:
        self._type = None
        self._name = name
        self._kind: ExpectationKind = kind
        self._times: Optional[int] = None
        self._arguments: Optional[Tuple] = None
        self._return_values: Union[object, List] = _UNSET
        self._calls = 0
        self._call_frame = None

    def times(self, times: int) -> "Expectation":
        self._times = times
        self._call_frame = inspect.stack()[1]

        return self

    def with_(self, *args, **kwargs) -> "Expectation":
        self._arguments = self._get_arguments(*args, **kwargs)

        return self

    def returns(self, *return_values: Any) -> "Expectation":
        self._return_values = list(return_values)

        return self

    def verify(self) -> None:
        if self._times is not None and self._calls != self._times:
            raise InvalidMockCallsCount(
                self._name, self._times, self._calls, frame=self._call_frame
            )

    def verify_call(self, *args, **kwargs) -> Any:
        self._increment_calls()

        if self._has_return_values():
            return self._consume_return_value()

    def match(self, *args, **kwargs) -> bool:
        arguments = self._get_arguments(*args, **kwargs)

        return self._arguments is None or arguments == self._arguments

    def _increment_calls(self, count: int = 1) -> "Expectation":
        self._calls += count

        return self

    def _has_return_values(self) -> bool:
        return self._return_values is not _UNSET

    def _consume_return_value(self) -> Any:
        value = self._return_values.pop(0)
        self._return_values.append(value)

        return value

    def _get_arguments(self, *args, **kwargs) -> Optional[Tuple]:
        if not args and not kwargs:
            return
        elif not kwargs:
            return args, None
        elif not args:
            return None, tuple(kwargs.items())
        else:
            return args, tuple(kwargs.items())
