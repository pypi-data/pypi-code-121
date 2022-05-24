# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring

class Token:

    """
    Token is the class that encapsulates a part of a source code: number, string or something else
    """

    Nil: str = 'Nil'
    Number: str = 'Number'
    String: str = 'String'
    Boolean: str = 'Boolean'
    Identifier: str = 'Identifier'
    OpeningBracket: str = 'OpeningBracket'
    ClosingBracket: str = 'ClosingBracket'

    _type: str
    _value: str

    def __init__(self, _type: str, _value: str) -> None:

        """Initializes Token instance"""

        self._type = _type
        self._value = _value

    def type(self) -> str:

        """Return token type"""

        return self._type

    def value(self) -> str:

        """Return token value"""

        return self._value

    def __str__(self) -> str:

        """Override __str__ method"""

        return f'Token<{self._type}>: {self._value}'

    def __repr__(self) -> str:

        """Override __repr__ method"""

        return self.__str__()  # in order to simplify debugging, make Token printing a bit fancier
