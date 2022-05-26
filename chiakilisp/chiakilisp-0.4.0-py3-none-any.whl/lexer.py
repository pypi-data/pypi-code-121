# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring

import re
from typing import List
from chiakilisp.models.token import Token  # Lexer needs Token :*)


ALPHABET = ['+', '-', '*', '/', '=', '<', '>', '?', '!', '.', '_', '&']


class Lexer:

    """
    Lexer is the class that takes source code and produces a list of tokens
    """

    _source: str
    _pointer: int
    _tokens: List[Token]

    def __init__(self, source: str) -> None:

        """Initialize Lexer instance"""

        self._source = source
        self._pointer = 0
        self._tokens = []

    def tokens(self) -> List[Token]:

        """Returns list of tokens"""

        return self._tokens

    def lex(self) -> None:  # pylint: disable=R0912, disable=R0915  # >_<

        """Process the source code, thus it populates the tokens list"""

        while self._has_next_symbol():

            if self._current_symbol_is_semicolon() or \
                    self._current_symbol_is_hash():
                self._advance()
                while self._has_next_symbol():
                    if self._current_symbol_is_nl():
                        break
                    self._advance()
                self._advance()

            elif self._current_symbol_is_number():
                value = self._current_symbol()
                self._advance()
                while self._has_next_symbol():
                    if self._current_symbol_is_number():
                        value += self._current_symbol()
                        self._advance()
                    else:
                        break
                self._tokens.append(Token(Token.Number, value))

            elif self._current_symbol_is_letter():
                value = self._current_symbol()
                self._advance()
                while self._has_next_symbol():
                    if self._current_symbol_is_letter() or \
                            self._current_symbol_is_number():
                        value += self._current_symbol()
                        self._advance()
                    else:
                        break
                if value == 'nil':
                    self._tokens.append(Token(Token.Nil, 'nil'))
                elif value in ['true', 'false']:
                    self._tokens.append(Token(Token.Boolean, value))
                else:
                    self._tokens.append(Token(Token.Identifier, value))

            elif self._current_symbol_is_double_quote():
                value = ''
                while self._has_next_symbol():
                    self._advance()
                    if not self._current_symbol_is_double_quote():
                        value += self._current_symbol()
                    else:
                        self._tokens.append(Token(Token.String, value))
                        break
                self._advance()  # _advance(): to skip leading '"' char

            elif self._current_symbol_is_opening_bracket():
                self._tokens.append(Token(Token.OpeningBracket,   '('))
                self._advance()

            elif self._current_symbol_is_closing_bracket():
                self._tokens.append(Token(Token.ClosingBracket,   ')'))
                self._advance()

            elif self._current_symbol_is_cr_opening_bracket():
                self._tokens.append(Token(Token.OpeningBracket,   '('))
                self._tokens.append(Token(Token.Identifier,   'dicty'))
                self._advance()

            elif self._current_symbol_is_cr_closing_bracket():
                self._tokens.append(Token(Token.ClosingBracket,   ')'))
                self._advance()

            elif self._current_symbol_is_sq_opening_bracket():
                self._tokens.append(Token(Token.OpeningBracket,   '('))
                self._tokens.append(Token(Token.Identifier,   'listy'))
                self._advance()

            elif self._current_symbol_is_sq_closing_bracket():
                self._tokens.append(Token(Token.ClosingBracket,   ')'))
                self._advance()

            else:
                self._advance()  # skip over all the garbage characters

    def _advance(self) -> None:

        """Advance the pointer"""

        self._pointer += 1

    def _current_symbol(self) -> str:

        """Returns the current symbol"""

        return self._source[self._pointer]

    def _has_next_symbol(self) -> bool:

        """Returns whether source has next symbol"""

        return self._pointer < len(self._source)

    def _current_symbol_is_nl(self) -> bool:

        """Returns whether current symbol is a newline symbol"""

        return self._current_symbol() == '\n'

    def _current_symbol_is_hash(self) -> bool:

        """Returns whether current symbol is a hashtag symbol"""

        return self._current_symbol() == '#'

    def _current_symbol_is_semicolon(self) -> bool:

        """Returns whether current symbol is a semicolon symbol"""

        return self._current_symbol() == ';'

    def _current_symbol_is_double_quote(self) -> bool:

        """Returns whether current symbol is a double-quote symbol"""

        return self._current_symbol() == '"'

    def _current_symbol_is_opening_bracket(self) -> bool:

        """Returns whether current symbol is an opening bracket symbol"""

        return self._current_symbol() == '('

    def _current_symbol_is_closing_bracket(self) -> bool:

        """Returns whether current symbol is a closing bracket symbol"""

        return self._current_symbol() == ')'

    def _current_symbol_is_cr_opening_bracket(self) -> bool:

        """Returns whether current symbol is a curly-opening bracket symbol"""

        return self._current_symbol() == '{'

    def _current_symbol_is_cr_closing_bracket(self) -> bool:

        """Returns whether current symbol is a curly-closing bracket symbol"""

        return self._current_symbol() == '}'

    def _current_symbol_is_sq_opening_bracket(self) -> bool:

        """Returns whether current symbol is a square-opening bracket symbol"""

        return self._current_symbol() == '['

    def _current_symbol_is_sq_closing_bracket(self) -> bool:

        """Returns whether current symbol is a square-closing bracket symbol"""

        return self._current_symbol() == ']'

    def _current_symbol_is_number(self) -> bool:

        """Returns whether current symbol is a number, valid number is from 0 to 9"""

        return re.match(r'[0-9]', self._current_symbol()) is not None

    def _current_symbol_is_letter(self) -> bool:

        """Returns whether current symbol is a letter: valid letter is from a-ZA-Z or from the alphabet"""

        return re.match(r'[a-zA-Z]', self._current_symbol()) is not None or self._current_symbol() in ALPHABET
