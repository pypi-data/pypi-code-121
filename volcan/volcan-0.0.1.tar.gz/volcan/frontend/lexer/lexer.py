from typing import Optional

from .keyword import KEYWORDS
from .symbol import SYMBOL_CHARS, SYMBOLS
from .token import Token, TokenMetadata, TokenType


class Lexer:
    __slots__ = (
        "_file",
        "_data",
        "_line",
        "_index",
    )

    def __init__(self, file: str, data: str) -> None:
        self._file = file
        self._data = data

        self._line = 1
        self._index = 0

    def _get_token(self, type: TokenType, value: Optional[str] = None) -> Token:
        return Token(type, value, TokenMetadata(self._file, self._line, self._index - (len(value) if value else 0)))

    def _match(self, value: str) -> bool:
        for i, char in enumerate(value):
            if i >= len(self._data) or self._data[self._index + i] != char:
                return False

        return True

    def _peek(self, offset: int = 0, length: int = 1) -> Optional[str]:
        if self._index + offset + length > len(self._data):
            return

        return self._data[self._index + offset : self._index + offset + length]

    def _read_number(self) -> Token:
        number = ""
        decimal = False

        while (char := self._peek()) in set("01234567890."):
            if char == ".":
                if decimal:
                    raise Exception("Invalid number: found unexpected decimal after existing decimal")

                decimal = True

            number += char
            self._index += 1

        return self._get_token(TokenType.NUMBER, number)

    def _read_string(self, quote: str) -> Token:
        string = ""
        escape = False
        closed = False

        while (char := self._peek(1)) is not None:
            if char == "\\":
                escape = True
            elif char == quote and not escape:
                self._index += 1
                closed = True
                break

            string += char
            self._index += 1

        if not closed:
            raise Exception("Unterminated string literal.")

        self._index += 1

        return self._get_token(TokenType.STRING, string)

    def _read_identifier(self) -> Token:
        identifier = ""

        while (char := self._peek()) is not None and char.isalnum():
            identifier += char
            self._index += 1

        if identifier in KEYWORDS:
            return self._get_token(getattr(TokenType, KEYWORDS[identifier]))

        return self._get_token(TokenType.IDENTIFIER, identifier)

    def _read_symbol(self) -> Token:
        symbol = ""

        while (char := self._peek()) is not None and char in SYMBOL_CHARS:
            symbol += char

            if symbol not in SYMBOLS:
                symbol = symbol[:-1]
                break

            self._index += 1

        if symbol in SYMBOLS:
            return self._get_token(getattr(TokenType, SYMBOLS[symbol]))

        raise Exception("Invalid symbol: " + symbol)

    def _read_comment(self) -> Token:
        comment = ""

        while (char := self._peek()) is not None and char != "\n":
            comment += char
            self._index += 1

        self._index += 1

        return self._get_token(TokenType.COMMENT, comment)

    def _read_token(self) -> Token:
        while (char := self._peek()) in [" ", "\n", "\r", "\t", None]:
            if char is None:
                return self._get_token(TokenType.EOF)

            if char == "\n":
                self._line += 1
            self._index += 1

        if char is None:
            return self._get_token(TokenType.EOF)

        if char in SYMBOL_CHARS:
            return self._read_symbol()

        if char.isdigit():
            return self._read_number()

        if char.isalpha():
            return self._read_identifier()

        if char in ["'", '"']:
            return self._read_string(char)

        if char == "#":
            return self._read_comment()

        raise Exception("Invalid character: " + char)

    def tokenise(self) -> list[Token]:
        tokens: list[Token] = []

        while True:
            token = self._read_token()
            tokens.append(token)

            if token.type is TokenType.EOF:
                break

        return tokens
