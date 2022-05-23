'''
PHP7+ EnumWriter

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

from typing import Any, TextIO

from buildtools.indentation import IndentWriter

from buildtools.maestro.enumwriters.types import EnumDefinition

from .enumwriter import EnumWriter


class PHPEnumWriter(EnumWriter):
    def __init__(self, compressed):
        super().__init__()
        self.compressed = compressed

    def get_config(self):
        return {'compressed': self.compressed}

    def write(self, _w: TextIO, ed: EnumDefinition):
        name = ed.name
        phpdef = ed.langconf.get('php', {})
        extends = phpdef.get('extends', 'SplEnum')
        namespace = phpdef.get('namespace', None)

        w = IndentWriter(_w, indent_chars='\t')

        def writeline(ln: str) -> None:
            nonlocal w, _w
            if self.compressed:
                _w.write(ln)
            else:
                w.writeline(ln)

        eq = '=' if self.compressed else ' = '

        def writeConst(name: str, value: Any) -> None:
            nonlocal eq
            writeline(f'const {name}{eq}{value!r};')

        writeline('<?php /* @generated */')
        if namespace is not None:
            writeline(f'namespace {namespace};')
        writeline(f'class {name} extends {extends} {{')
        with w:
            writeConst('__default', ed.default)
            if ed.is_flags:
                writeConst('NONE', 0)
                if not self.compressed:
                    w.writeline(f'//  b{ed.all_flags:032b}')
                    w.writeline(f'// 0x{ed.all_flags:08X}')
                writeConst('ALL', ed.all_flags)
            else:
                writeConst('MIN', ed.min)
                writeConst('MAX', ed.max)
                # if not self.compressed:
                #    w.writeline()

            for k, v in ed.values.items():
                if v.meaning:
                    if self.compressed:
                        _w.write(f'/* {v.meaning} */')
                    else:
                        writeline('/**')
                        for ln in v.meaning.splitlines():
                            writeline(f' * {ln.strip()}')
                        writeline(' */')
                writeConst(v.id, v.value)

            if ed.is_flags:
                writeline('public static function ValueToStrings(int $val) {')
                with w:
                    writeline('$o=[];')
                    if self.compressed:
                        _w.write('for($bitidx=0;$bitidx<32;$bitidx++){')
                    else:
                        w.writeline(
                            'for($bitidx = 0; $bitidx < 32; $bitidx++) {')
                    with w:
                        if self.compressed:
                            _w.write('switch($val&(1<<$bitidx)){')
                        else:
                            w.writeline('switch ($val & (1 << $bitidx)) {')
                        with w:
                            for k, v in ed.values.items():
                                writeline(f'case {v.value!r}:')
                                with w:
                                    if self.compressed:
                                        _w.write(f'$o[]={k!r};')
                                    else:
                                        w.writeline(f'$o []= {k!r}')
                                    writeline('break;')
                        writeline('}')  # switch($val)
                    writeline('}')  # for($bitidx=1;$i<32;$i++)
                    writeline('return $o;')
                writeline('}')

            writeline(
                'public static function ValueToString(int $val, string $sep=",", string $start_end=""){')
            if not ed.is_flags:
                with w:
                    writeline('$o=null;')
                    writeline(
                        'switch($val){' if self.compressed else 'switch ($val) {')
                    with w:
                        for k, v in ed.values.items():
                            writeline(f'case {v!r}:')
                            with w:
                                writeline(
                                    f'$o={k!r};' if self.compressed else '$o = {k!r};')
                                writeline('break;')
                    writeline('}')  # switch($val)
            else:
                writeline(
                    '$o=implode($sep,self::ValueToStrings($val));' if self.compressed else '$o = implode($sep, self::ValueToStrings($val));')
            if self.compressed:
                _w.write('if(strlen($start_end)==2)')
                _w.write('$o=substr($start_end,0,1).$o.substr($start_end,1,1);')
                _w.write('return $o;')
            else:
                with w.writeline('if (strlen($start_end) == 2) {'):
                    w.writeline(
                        '$o = substr($start_end, 0, 1) . $o . substr($start_end, 1, 1);')
                w.writeline('}')
            writeline('}')  # ValueToString

            writeline('public static function StringToValue(string $key){')
            with w:
                writeline(
                    'switch($key){' if self.compressed else 'switch ($key) {')
                with w:
                    for k, v in ed.values.items():
                        writeline(f'case {k!r}:')
                        with w:
                            writeline(f'return {v!r};')
                writeline('}')  # switch($val)
                writeline('return {ed.error!r};')
            writeline('}')  # StringToValue

            writeline('public static function Keys() {')
            with w:
                writeline(f'return {list(ed.values.keys())!r};')
            writeline('}')  # Keys()

            writeline('public static function Values() {')
            with w:
                writeline(f'return {list(ed.values.values())!r};')
            writeline('}')  # Values()

            writeline('public static function Count() {')
            with w:
                writeline(f'return {len(ed.values.keys())!r};')
            writeline('}')  # Count()

            if not ed.is_flags:
                writeline('public static function Width() {')
                with w:
                    writeline(f'return {ed.max.bit_length()};')
                writeline('}')  # Width()
        writeline('}')
