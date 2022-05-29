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
import dataclasses
from typing import Dict, Optional, Union

WORDS = 'abcdefghijklmnopqrstuvwxyz'

TOKEN_KINDS: Dict[str, Dict[str, Union[bool, str]]] = {
    # TOKEN-PAREN-TYPE: Single Line
    'Semi': {'multi-line': False, 'letter': ';'},
    'Comma': {'multi-line': False, 'letter': ','},
    'LineComment': {'multi-line': False, 'letter': '#'},
    'Dot': {'multi-line': False, 'letter': '.'},
    'OpenParen': {'multi-line': False, 'letter': '('},
    'CloseParen': {'multi-line': False, 'letter': ')'},
    'OpenBrace': {'multi-line': False, 'letter': '{'},
    'CloseBrace': {'multi-line': False, 'letter': '}'},
    'OpenBracket': {'multi-line': False, 'letter': '['},
    'CloseBracket': {'multi-line': False, 'letter': ']'},
    'At': {'multi-line': False, 'letter': '@'},
    'Tilde': {'multi-line': False, 'letter': '~'},
    'Question': {'multi-line': False, 'letter': '?'},
    'Colon': {'multi-line': False, 'letter': ':'},
    'Dollar': {'multi-line': False, 'letter': '$'},
    'Eq': {'multi-line': False, 'letter': '='},
    'Bang': {'multi-line': False, 'letter': '!'},
    'Lt': {'multi-line': False, 'letter': '<'},
    'Gt': {'multi-line': False, 'letter': '>'},
    'Minus': {'multi-line': False, 'letter': '-'},
    'Plus': {'multi-line': False, 'letter': '+'},
    'Percent': {'multi-line': False, 'letter': '%'},
    'WhiteSpace': {'multi-line': False, 'letter': ' '},
    'SingleQuote': {'multi-line': False, 'letter': "'"},
    'DoubleQuote': {'multi-line': False, 'letter': '"'},
}


@dataclasses.dataclass
class Token:
    kind: str
    content: Optional[str] = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'kind: {self.kind}\ncontent: {self.content or ""}'
