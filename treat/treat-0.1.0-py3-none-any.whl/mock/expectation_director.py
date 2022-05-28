import types

from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from treat.mock.exceptions import MockError
from treat.mock.expectation import Expectation
from treat.mock.expectation import ExpectationKind


if TYPE_CHECKING:
    from treat.mock.mock import Mock


class ExpectationDirector:
    def __init__(self, name: str, mock: "Mock") -> None:
        if not hasattr(mock.mocked, name):
            raise MockError(f'{mock.mocked} does not have an attribute named "{name}".')

        self._name: str = name
        self._mock: "Mock" = mock
        self._original = object.__getattribute__(mock.mocked, name)
        self._expectations: List[Expectation] = []
        self._is_setup: bool = False
        self._local_override: bool = False

    def add_expectation(self, expectation: Expectation) -> None:
        self._expectations.append(expectation)

    def setup(self) -> None:
        if self._is_setup:
            return

        if issubclass(self._original.__class__, (types.FunctionType, types.MethodType)):
            self._set(
                types.MethodType(self.caller(ExpectationKind.METHOD), self._mock.mocked)
            )
        elif issubclass(self._original.__class__, property):
            self._set(self.caller(ExpectationKind.PROPERTY))
        else:
            self._set(self.caller(ExpectationKind.ATTRIBUTE))

    def teardown(self) -> None:
        self._unset()

    def caller(self, kind: ExpectationKind) -> Callable:
        if kind is ExpectationKind.METHOD:

            def caller(self_, *args, **kwargs):
                return self.call(*args, **kwargs)

        elif kind is ExpectationKind.PROPERTY:

            @property
            def caller(self_, *args, **kwargs):
                return self.call(self_, *args, **kwargs)

        else:

            @property
            def caller(self_, *args, **kwargs):
                return self.call(self_, *args, **kwargs)

        return caller

    def call(self, *args, **kwargs) -> Any:
        expectation = self.find_expectation(*args, **kwargs)

        if not expectation:
            return self._original(self._mock.mocked, *args, **kwargs)

        return expectation.verify_call(*args, **kwargs)

    def find_expectation(self, *args, **kwargs) -> Optional[Expectation]:
        for expectation in self._expectations:
            if expectation.match(*args, **kwargs):
                return expectation

    def verify(self) -> None:
        for expectation in self._expectations:
            expectation.verify()

    def _set(self, value: Any) -> None:
        local_override = False

        if (
            hasattr(self._mock.mocked, "__dict__")
            and type(self._mock.mocked.__dict__) is dict
        ):
            if self._name not in self._mock.mocked.__dict__:
                local_override = True

            self._mock.mocked.__dict__[self._name] = value
        else:
            setattr(self._mock.mocked, self._name, value)

        self._local_override = local_override

    def _unset(self) -> None:
        if (
            hasattr(self._mock.mocked, "__dict__")
            and self._name in self._mock.mocked.__dict__
            and type(self._mock.mocked.__dict__) is dict
        ):
            if self._local_override:
                del self._mock.mocked.__dict__[self._name]
            else:
                self._mock.mocked.__dict__[self._name] = self._original
        else:
            setattr(self._mock.mocked, self._name, self._original)
