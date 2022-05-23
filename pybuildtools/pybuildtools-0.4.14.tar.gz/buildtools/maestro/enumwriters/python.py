'''
Enum code generator for Python 3+.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from buildtools.indentation import IndentWriter
from .enumwriter import EnumWriter
from typing import Any, TextIO

from buildtools.maestro.enumwriters.types import EnumDefinition


class PythonEnumWriter(EnumWriter):
    def _writeStaticConst(self, w: IndentWriter, key: str, value: Any) -> None:
        w.writeline(f'{key} = {value!r}')

    def write(self, _w: TextIO, ed: EnumDefinition):
        name = ed.name
        pydef = ed.langconf.get('python', {})
        w = IndentWriter(_w, indent_chars='    ')
        w.writeline('# @generated')
        w.writeline('import enum')
        for imp in pydef.get('imports', []):
            if isinstance(imp, dict):
                k, v = next(iter(imp.items()))
                if isinstance(v, list):
                    w.writeline(f'from {k} import ({", ".join(sorted(v))})')
                else:
                    w.writeline(f'from {k} import {v}')
            if isinstance(imp, str):
                w.writeline(f'import {imp}')
        w.writeline(f'__all__ = [{name!r}]')
        defaultInherits = ['enum.IntEnum']
        if ed.is_flags:
            defaultInherits = ['enum.IntFlags']
        inherits = pydef.get('inherits', defaultInherits)
        with w.writeline(f'class {name}({", ".join(inherits)}):'):
            if ed.is_flags:
                self._writeStaticConst(w, 'NONE', 0)

            for k, v in ed.values.items():
                if v.meaning and len(v.meaning) > 0:
                    w.writeline("'''")
                    w.writeline(v.meaning)
                    w.writeline("'''")
                self._writeStaticConst(w, k, v.value)

        if not ed.is_flags:
            w.writeline(f'{name}.MIN = {ed.min!r}')
            w.writeline(f'{name}.MAX = {ed.max!r}')
            w.writeline(f'{name}.WIDTH = {ed.max.bit_length()!r}')
            pass
        else:
            w.writeline("'''")
            w.writeline(f' b{ed.all_flags:032b}')
            w.writeline(f'0x{ed.all_flags:0X}')
            w.writeline("'''")
            w.writeline(f'{name}.ALL = {ed.all_flags!r}')
