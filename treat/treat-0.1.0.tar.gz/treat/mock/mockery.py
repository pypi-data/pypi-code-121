from typing import Dict
from typing import NoReturn
from typing import Type

from treat.mock.mock import Mock


class Mockery:
    def __init__(self) -> None:
        self._mocks: Dict[Type, Mock] = {}

    def mock(self, obj: Type) -> Mock:
        if obj in self._mocks:
            return self._mocks[obj]

        self._mocks[obj] = Mock(obj)

        return self._mocks[obj]

    def close(self) -> NoReturn:
        self._verify()

    def _verify(self) -> None:
        try:
            for mock in self._mocks.values():
                mock.verify()
        finally:
            self._reset()

    def _reset(self) -> None:
        for mock in self._mocks.values():
            mock.reset()

        self._mocks = {}
