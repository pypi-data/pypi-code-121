# MIT License
#
# Copyright (c) 2022 Venera Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from dataclasses import dataclass
from typing import List

from .errors import BadToken
from .token import TOKEN_KINDS, WORDS, Token


@dataclass
class Tokenizer:
    code: str
    filename: str

    def start(self) -> List[Token]:
        TOKEN_KINDS_RAW = []
        TOKENS = []

        for kind in TOKEN_KINDS.values():
            TOKEN_KINDS_RAW.append(kind['letter'])

        LAST_TK = ''

        for tk in self.code:
            if LAST_TK == '\/' and tk == 'n' or tk == ';':
                TOKENS.append(Token('Indent'))
                continue

            if (
                tk not in TOKEN_KINDS_RAW
                and tk not in WORDS
                and tk not in WORDS.upper()
                and tk not in '; \n'.split(' ')
            ):
                raise BadToken(
                    f'Token "{tk}" in file {self.filename} is not supported.'
                )

            if tk in WORDS or tk in WORDS.upper():
                TOKENS.append(Token('Word', tk))
                continue

            for kindname, kind in TOKEN_KINDS.items():
                if tk == kind['letter']:
                    TOKENS.append(Token(kindname, tk))

            LAST_TK = tk

        return TOKENS
