'''
CoffeeScript enum writer

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

import json
from typing import TextIO

from buildtools.indentation import IndentWriter

from buildtools.maestro.enumwriters.types import EnumDefinition, EnumValueInfo

from .enumwriter import EnumWriter


class CoffeeEnumWriter(EnumWriter):
    def __init__(self):
        super().__init__()

    def write(self, _w: TextIO, ed: EnumDefinition) -> None:
        coffeedef = ed.langconf.get('coffee', {})
        valcount = len(ed.values.keys())

        w = IndentWriter(_w,
                         indent_chars=coffeedef.get('indent_chars', '    '))

        w.writeline('###')
        if ed.notes:
            for line in ed.notes.split('\n'):
                w.writeline(f'# {line.strip()}')
        w.writeline(f'# @enumdef: {ed.name}')
        w.writeline(f'###')
        with w.writeline(f'export class {ed.name}' if coffeedef.get('export', False) else f'class {ed.name}'):
            w.writeline(f'@_DEFAULT: {ed.default!r}')
            w.writeline(f'@_ERROR: {ed.error!r}')

            if ed.is_flags:
                w.writeline('@NONE: 0')

            vpak: EnumValueInfo
            for k, vpak in ed.values.items():
                if vpak.meaning:
                    w.writeline('###')
                    w.writeline('# ' + json.dumps(vpak.meaning.strip()))
                    w.writeline('###')
                w.writeline(f'@{vpak.id}: {json.dumps(vpak.value)}')

            if ed.is_flags:
                w.writeline()
                with w.writeline('@ValueToStrings: (val) ->'):
                    w.writeline('o = []')
                    with w.writeline(f'for bitidx in [0...{valcount}]'):
                        w.writeline('switch (1 << bitidx) & val')
                        written = set()
                        for k, v in ed.values.items():
                            jk = json.dumps(k)
                            jv = json.dumps(v.value)
                            if v.value in written:
                                continue
                            written.add(v.value)
                            with w.writeline(f'when {jv}'):
                                w.writeline(f'o.push {jk}')
                        w.writeline('o')

                w.writeline()
                with w.writeline('@StringsToValue: (valarr) ->'):
                    with w.writeline('o = 0'):
                        with w.writeline('for flagname in valarr'):
                            w.writeline('o |= @StringToValue flagname')
                    w.writeline('o')

            w.writeline()
            with w.writeline('@ValueToString: (val, sep=", ", start_end="") ->'):
                if ed.is_flags:
                    w.writeline('return @ValueToStrings(val).join sep')
                else:
                    w.writeline('o = null')
                    with w.writeline('switch val'):
                        written = set()
                        for k, v in ed.values.items():
                            if v.value in written:
                                continue
                            written.add(v.value)
                            jk = json.dumps(k)
                            jv = json.dumps(v.value)
                            with w.writeline(f'when {jv}'):
                                w.writeline(f'o = {jk}')
                    with w.writeline('if start_end.length == 1'):
                        w.writeline('return start_end + o + start_end')
                    with w.writeline('if start_end.length == 2'):
                        w.writeline('return start_end[0] + o + start_end[1]')
                    w.writeline('o')

            w.writeline()
            with w.writeline('@StringToValue: (key) ->'):
                with w.writeline('switch key'):
                    written = set()
                    for k, v in ed.values.items():
                        if k in written:
                            continue
                        written.add(k)
                        jk = json.dumps(k)
                        jv = json.dumps(v.value)
                        with w.writeline(f'when {jk}'):
                            w.writeline(f'return {jv}')
                w.writeline(f'{json.dumps(ed.error)}')

            w.writeline()
            keys = ', '.join([json.dumps(x) for x in ed.values.keys()])
            w.writeline(f'@Keys: -> [{keys}]')

            w.writeline()
            values = ', '.join([json.dumps(v.value)
                               for v in ed.values.values()])
            w.writeline(f'@Values: -> [{values}]')

            w.writeline()
            w.writeline(f'@Count: -> {valcount}')

            if not ed.is_flags:
                w.writeline()
                w.writeline(f'@Min: -> {json.dumps(ed.min)}')

                w.writeline()
                w.writeline(f'@Max: -> {json.dumps(ed.max)}')

            else:
                allofem = 0
                for v in ed.values.values():
                    allofem |= int(v.value)
                w.writeline()
                w.writeline(f'@All: -> {json.dumps(allofem)}')

            w.writeline()
            w.writeline(f'@Width: -> {json.dumps(ed.max.bit_length())}')
