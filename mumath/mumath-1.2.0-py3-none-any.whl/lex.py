import xml.etree.ElementTree as ET
import re
import io
from typing import NamedTuple
from itertools import chain
from .context.tokens import tok_name

try:
    from functools import cache
except importError:
    from functools import lru_cache as cache

# fun equivalent
# def TokenInfo(type: str, string: str, start: str, end: int, line: int): pass
# TokenInfo = NamedTuple(TokenInfo.__name__, TokenInfo.__annotations__)

# shamelessly copied from python.tokenize, with an added flag
_TokenInfo = NamedTuple("TokenInfo", [
    ("type", int),
    ("variant", int),
    ("string", str),
    ("start", int),
    ("end", int),
    ("line", int),
    ("flag", int),
])


# Match words without _ and numbers
_keyword = re.compile(r"\\[^\W\d_]+")


class TokenInfo(_TokenInfo):
    def __repr__(self):
        return ('TokenInfo(type=%s, variant=%s, string=%r, start=%r, end=%r, line=%r, flag=%s)' %
                self._replace(type=tok_name[self.type]))


def _token_error_msg(line, pos):
    return "\n".join(["Unknown token:", line, " "*pos + "^"*(len(line) - pos)])


class Lexer:
    def __init__(self, symbols, keywords={}, flags={}):
        self.symbols = symbols
        self.types = list(symbols.values())
        self.keywords = keywords
        self.flags = flags

        self.pattern = re.compile("|".join(
            f"({pattern})" for pattern in symbols
        ), flags=re.UNICODE)

    @classmethod
    @cache
    def from_glyph(cls, glyph):
        symbols = {_keyword.pattern: None}
        keywords = {}
        for ijk, ttype, pattern in glyph.patterns():
            if _keyword.fullmatch(pattern):
                keywords[pattern] = (ttype, ijk)
            else:
                symbols[pattern] = (ttype, ijk)

        return cls(symbols, keywords, glyph.flags)

    def _tokenize(self, stream):
        flag = 0
        for lineno, line in enumerate(stream, start=1):
            pos = 0
            while m := self.pattern.match(line, pos):
                # lastindex is 1-indexed
                tindex, token, start, end =\
                    m.lastindex, m.group(), m.start(), m.end()

                if token in self.keywords:
                    ttype, variant = self.keywords[token]
                else:
                    ttype, variant = self.types[tindex-1]

                if setter := self.flags.get(ttype):
                    flag = setter(flag)
                    pos = end
                    continue

                token = TokenInfo(ttype, variant, token, start, end, lineno, flag)

                yield token
                pos = end

                # if start == end: raise ValueError("Zero-width token")
            if pos != len(line):
                raise ValueError(_token_error_msg(line, pos))

    def tokenize(self, stream):
        if isinstance(stream, str):
            stream = io.StringIO(stream)
        return self._tokenize(stream)
