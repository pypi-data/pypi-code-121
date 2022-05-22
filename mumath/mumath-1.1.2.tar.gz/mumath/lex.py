import xml.etree.ElementTree as ET
import re
import io
from typing import NamedTuple
from itertools import chain
from .context.tokens import tok_name

# fun equivalent
# def TokenInfo(type: str, string: str, start: str, end: int, line: int): pass
# TokenInfo = NamedTuple(TokenInfo.__name__, TokenInfo.__annotations__)

# shamelessly copied from python.tokenize, with an added flag
_TokenInfo = NamedTuple("TokenInfo", [
    ("type", int),
    ("string", str),
    ("start", int),
    ("end", int),
    ("line", int),
    ("flag", int),
])

class TokenInfo(_TokenInfo):
    def __repr__(self):
        return ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r, flag=%s)' %
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
    def from_glyph(cls, glyph):
        return cls(glyph.tokens, glyph.keywords, glyph.flags)

    def _tokenize(self, stream):
        if isinstance(stream, str):
            stream = io.StringIO(stream)

        flag = 0
        for lineno, line in enumerate(stream, start=1):
            pos = 0
            while m := self.pattern.match(line, pos):
                # lastindex is 1-indexed
                tindex, token, start, end =\
                    m.lastindex, m.group(), m.start(), m.end()
                ttype = self.types[tindex-1]

                if setter := self.flags.get(ttype):
                    flag = setter(flag)
                    pos = end
                    continue

                ttype = self.keywords.get(token, ttype)
                token = TokenInfo(ttype, token, start, end, lineno, flag)

                yield token
                pos = end

                # if start == end: raise ValueError("Zero-width token")
            if pos != len(line):
                raise ValueError(_token_error_msg(line, pos))

    def tokenize(self, stream):
        return self._tokenize(stream)


# class Lookahead:
#     def __init__(self, it):
#         self._it = iter(it)

#     def __iter__(self):
#         return self

#     def __next__(self):
#         return next(self._it)

#     def peek(self, default=None):
#         it = self._it
#         try:
#             v = next(self._it)
#             self._it = chain((v,), it)
#             return v
#         except StopIteration:
#             return default
