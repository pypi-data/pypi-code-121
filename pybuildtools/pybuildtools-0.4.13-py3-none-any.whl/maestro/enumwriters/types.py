'''
Enum Code Generation Utility Types

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

import collections
from enum import IntEnum
import random
import sys
from typing import Any, Callable, Dict, List, Optional, OrderedDict, Set
from buildtools import log


_count_bits: Callable[[int], int]
if hasattr(int, 'bit_count'):
    def _count_bits(v: int): return v.bit_count()
else:
    # https://stackoverflow.com/questions/9829578/fast-way-of-counting-non-zero-bits-in-positive-integer
    # Yes, this is literally faster than bitshifting. sigh. (until 3.10)
    def _count_bits(v: int): return bin(v).count('1')


class EnumValueInfo:
    def __init__(self) -> None:
        self.id: str = ''
        self.value: Optional[int] = None
        self.no_scramble: bool = False
        self.default: bool = False
        self.meaning: Optional[str] = None

    def deserialize(self, id: str, data: dict) -> None:
        self.id = id
        if not isinstance(data, dict):
            data = {'value': data}
        self.value = data.get('value', None)
        if data.get('auto', False):
            self.value = None
        self.no_scramble = data.get('no-scramble', False)
        self.default = data.get('default', False)
        self.meaning = data.get('meaning')


class EIncrementType(IntEnum):
    DECIMAL = 0
    BINARY = 1


class AutoValueInfo:
    def __init__(self) -> None:
        self.enabled: bool = False
        self.start: int = 0
        self.step: int = 1
        self.increment_type: EIncrementType = EIncrementType.DECIMAL

        self.__current: Optional[int] = None

    def deserialize(self, data: dict) -> None:
        self.enabled = data is not None
        if self.enabled:
            self.start = data.get('start', 0)
            self.step = data.get('step', 1)

    def getvalue(self) -> int:
        if self.__current is None:
            self.__current = self.start
        o = self.__current
        if self.increment_type == EIncrementType.DECIMAL:
            self.__current += self.step
        elif self.increment_type == EIncrementType.BINARY:
            self.__current <<= self.step
        return o


class EnumTestInfo:
    def __init__(self) -> None:
        self.are_unique: bool = False
        self.are_single_bit_only: bool = False
        self.increment_start: Optional[int] = None
        self.increment_stop: Optional[int] = None
        self.increment_step: Optional[int] = None

    def deserialize(self, data: dict) -> None:
        self.are_unique = data.get('unique', False)
        self.are_single_bit_only = data.get('single-bit-only', False)
        incr = data.get('increment', {})
        self.increment_start = incr.get('start')
        self.increment_stop = incr.get('stop')
        self.increment_step = incr.get('step')

    def test(self, enumdef: 'EnumDefinition') -> None:
        if self.increment_start and self.increment_stop:
            r: range
            if self.increment_step:
                r = range(self.increment_start,
                          self.increment_stop, self.increment_step)
            else:
                r = range(self.increment_start, self.increment_stop)
            defined = set([x.value for x in enumdef.values.values()])
            for i in r:
                if enumdef.is_flags:
                    if (1 << i) not in defined:
                        log.critical('increment: Missing value %d!', 1 << i)
                        sys.exit(1)
                else:
                    if i not in defined:
                        log.critical('increment: Missing value %d!', i)
                        sys.exit(1)
        known: Dict[int, str] = {}
        v: EnumValueInfo
        for k, v in enumdef.values.items():
            if self.are_single_bit_only:
                bc = _count_bits(v.value)
                if bc != 1:
                    log.critical(
                        f'are-single-bit: {k} has {bc} set bits instead of 1.')
                    sys.exit(1)
            if self.are_unique:
                if v.value in known.keys():
                    otherk = known[v.value]
                    log.critical(
                        f'unique: {k} and {otherk} have the same value.')
                    sys.exit(1)
                known[v.value] = k


class EnumDefinition:
    def __init__(self) -> None:
        self.is_scrambled: bool = False
        self.is_flags: bool = False
        self.auto_value: AutoValueInfo = AutoValueInfo()
        self.tests: EnumTestInfo = EnumTestInfo()
        self.values: OrderedDict[str,
                                 EnumValueInfo] = collections.OrderedDict()
        self.default: Optional[int] = None
        self.all_flags: Optional[int] = None
        self.error: Optional[int] = None
        self.name: str = ''
        self.langconf: Dict[str, Any] = {}
        self.notes: Optional[str] = None
        self.min: Optional[int] = None
        self.max: Optional[int] = None

    def deserialize(self, data: Dict[str, Any]) -> None:
        self.name = data['name']
        self.is_scrambled = data.get('scramble', False)
        self.is_flags = data.get('flags', False)
        self.is_flags = data.get('flags', False)
        self.default = data.get('default', 0)
        self.error = data.get('error', -1)
        self.langconf = data.get('lang', {})
        self.notes = data.get('notes')
        for dirname in ('coffee', 'php', 'python'):
            if dirname in data:
                log.warning(
                    f'The {dirname} directive is deprecated. Move {dirname} inside of a new lang directive.')
                self.langconf[dirname] = data[dirname]
                del data[dirname]
        if self.is_flags:
            self.tests.are_single_bit_only = True
            self.tests.are_unique = True
            self.auto_value.increment_type = EIncrementType.BINARY
            self.all_flags = 0
        else:
            self.min = 0
            self.max = 0
        if 'auto-value' in data:
            self.auto_value.deserialize(data['auto-value'])
        if 'tests' in data:
            self.tests.deserialize(data['tests'])
        numeric: bool = True
        for k, v in data['values'].items():
            ev = EnumValueInfo()
            ev.deserialize(k, v)
            if ev.value is None and self.auto_value.enabled:
                ev.value = self.auto_value.getvalue()
            self.values[ev.id] = ev
            if ev.default:
                self.default = ev.value
            if not isinstance(ev.value, int):
                numeric = False
            if numeric:
                if self.is_flags:
                    self.all_flags |= ev.value
        if numeric:
            vals: Set[int] = set([v.value for v in self.values.values()])
            if self.is_scrambled:
                valuesleft: List[int] = list(vals.copy())
                for v in self.values.values():
                    v.value = random.choice(valuesleft)
                    valuesleft.remove(v.value)
                    if ev.default:
                        self.default = ev.value
            self.min = min(vals)
            self.max = max(vals)
