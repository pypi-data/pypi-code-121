# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring

from typing import Any
from chiakilisp.models.token import Token  # Operand needs Token :*)


class NotFound:  # pylint: disable=too-few-public-methods  # shut up!

    """
    Stub class to display that there is no such a name in environment
    """


class Operand:

    """
    Operand is the class that encapsulates single Token and meant to be a prt of Expression (but not always)
    """

    _token: Token

    def __init__(self, token: Token) -> None:

        """Initialize Operand instance"""

        self._token = token

    def token(self) -> Token:

        """Returns related token"""

        return self._token

    def execute(self, environment: dict, __=False) -> Any:  # pylint: disable=inconsistent-return-statements

        """Execute here, is the return Python value related to the operand: string, number and vice versa"""

        if self.token().type() == Token.Nil:

            return None

        if self.token().type() == Token.Number:

            return int(self.token().value())

        if self.token().type() == Token.String:

            return self.token().value()

        if self.token().type() == Token.Boolean:

            return self.token().value() == 'true'

        if self.token().type() == Token.Identifier:

            name = self.token().value()
            found = environment.get(name, NotFound)

            if found is NotFound and '/' in self.token().value():
                _object, member = self.token().value().split('/')
                _object = environment.get(_object, NotFound)
                assert _object is not NotFound,   'Expression::execute(): qualified identifier lookup error'
                member = getattr(_object, member, NotFound)
                assert member is not NotFound,    'Expression::execute(): qualified identifier lookup error'
                return member  # <--------------------------- thus we return member of an object or a module

            assert found is not NotFound, f'Operand::execute(): no {name} in the current environment, typo?'

            return found  # return found Python 3 value (from the current environment), if not found, raise!
