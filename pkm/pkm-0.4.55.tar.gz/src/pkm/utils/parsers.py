import os
from typing import Optional, NoReturn, Callable, List, Type, TypeVar

_URL_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%")
_P = TypeVar("_P", bound="SimpleParser")
_T = TypeVar("_T")


class SimpleParser:
    """
    simple base class for parsers.
    functions semantics:
        match* -> return the matched data, if nothing matched return the empty string
        read* -> return a complex object resulted by parsing the content,
                 if cannot create the requested object raise error
    """

    def __init__(self, text: str, file_name: Optional[str] = None):
        self.text = text
        self.file_name = file_name
        self.position = 0

    def peek(self, amount: int = 1) -> str:
        p = self.position
        return self.text[p:p + amount]

    def is_not_empty(self) -> bool:
        return self.position < len(self.text)

    def is_empty(self) -> bool:
        return self.position == len(self.text)

    def read_digits(self) -> str:
        position = self.position
        self.until(lambda i, t: not t[i].isdigit())
        if self.position == position:
            self.raise_err('expecting digits')
        return self.text[position:self.position]

    def subparser(self, pareser_t: Type[_P]) -> _P:
        main_parser = self
        p = self.position

        class SubParser(pareser_t):
            @property
            def position(self) -> int:
                return main_parser.position

            @position.setter
            def position(self, v: int):
                main_parser.position = v

        result = SubParser(text=self.text)
        self.position = p
        return result

    def read_url(self, supported_schemas: Optional[List[str]] = None) -> str:
        p = self.position

        supported_schemas = supported_schemas or ['http', 'https']
        if not self.match_any(*supported_schemas):
            self.raise_err('expecting url')

        self.match_or_err('://', 'malformed url')
        self.until(lambda i, t: t[i] not in _URL_CHARS)

        return self.text[p:self.position]

    def match(self, *substrs: str) -> Optional[str]:
        p = self.position
        for i, substr in enumerate(substrs):
            if i != 0:
                self.match_ws(False)

            if self.peek(len(substr)) != substr:
                self.position = p
                return None

            self.position += len(substr)

        return self.text[p:self.position]

    def peek_prev(self, amount: int = 1) -> str:
        p = self.position
        start = max(0, p - amount)
        return self.text[start:p]

    def match_any(self, *substrs: str) -> Optional[str]:
        for substr in substrs:
            if self.match(substr):
                return substr

        return None

    def raise_err(self, msg: str, lines_to_show: int = 4) -> NoReturn:
        lines = self.text.splitlines(keepends=True)
        current_line = self.text.count('\n', 0, self.position)
        start_line = max(0, current_line - lines_to_show)
        sub_line_len = self.position - sum(len(it) for it in lines[:current_line])
        largest_line_len = max(len(lines[i]) if i < len(lines) else 0 for i in range(start_line, current_line + 1))
        pref = f'... after {start_line} lines ...\n\n' if start_line > 0 else ''
        largest_line_len = max(largest_line_len, len(pref))

        position_indicator = f"AT LINE {current_line}"
        if self.file_name:
            position_indicator = f"{self.file_name}:{current_line}"

        lines = ''.join(lines[start_line:current_line + 1])
        if not lines.endswith('\n'):
            lines += '\n'

        out = f"Parsing Failed: {msg} ({position_indicator})\n" \
              f"{'-' * largest_line_len}\n" \
              f"{pref}" \
              f"{lines}" \
              f"{'~' * sub_line_len}^"

        raise ValueError(out)

    def until_match(self, substr: str) -> str:
        pos = self.position

        try:
            self.position = self.text.index(substr, pos)
            return self.text[pos: self.position]
        except ValueError:
            return ''

    def until(self, predicate: Callable[[int, str], bool]) -> str:
        """
        match chars from this parser until `predicate` return True
        :param predicate: the stop condition to evaluate
        :return: the matched chars
        """
        p = self.position
        for i in range(self.position, len(self.text)):
            if predicate(i, self.text):
                self.position = i
                return self.text[p:i]

        self.position = len(self.text)
        return self.text[p:self.position]

    def next(self, amount: int = 1) -> str:
        peek = self.peek(amount)
        self.position += len(peek)

        return peek

    def match_or_err(self, substr: str, err: str) -> None:
        if not self.match(substr):
            self.raise_err(err)

    def __str__(self):
        return f"TextReader(pos={self.position}, '{self.text[self.position: self.position + 25]}...')"

    def __repr__(self):
        return str(self)

    def match_line(self, include_line_end: bool = True) -> str:
        result = self.until_match(os.linesep)
        if include_line_end:
            result += os.linesep
            self.position += len(os.linesep)
        return result

    def read_blank_line(self, include_line_end: bool = True):
        if content := self.match_line(include_line_end).strip():
            self.raise_err(f'unexpected content: {content}')

    def match_ws(self, allow_new_lines: bool = True) -> str:
        p = self.position
        while self.is_not_empty():
            n = self.peek()
            if n == '\n' and not allow_new_lines:
                break
            elif not n.isspace():
                break

            self.next()

        return self.text[p:self.position]
