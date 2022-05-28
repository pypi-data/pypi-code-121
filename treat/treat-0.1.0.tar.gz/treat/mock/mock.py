from typing import Dict
from typing import Type

from treat.mock.expectation import Expectation
from treat.mock.expectation import ExpectationKind
from treat.mock.expectation_director import ExpectationDirector
from treat.utils._compat import ReversableDict


class Mock:
    def __init__(self, mocked: Type) -> None:
        self._mocked: Type = mocked
        self._expectation_directors: Dict[str, ExpectationDirector] = ReversableDict()

    @property
    def mocked(self) -> Type:
        return self._mocked

    def expects(self, name: str) -> Expectation:
        if name not in self._expectation_directors:
            director = ExpectationDirector(name, self)
            director.setup()

            self._expectation_directors[name] = director

        expectation = Expectation(name, ExpectationKind.METHOD)
        self._expectation_directors[name].add_expectation(expectation)

        return expectation

    def verify(self) -> None:
        for director in self._expectation_directors.values():
            director.verify()

    def reset(self) -> None:
        for director in reversed(self._expectation_directors.values()):
            director.teardown()
