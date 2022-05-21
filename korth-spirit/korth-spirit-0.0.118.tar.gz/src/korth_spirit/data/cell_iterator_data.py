# Copyright (c) 2021-2022 Johnathan P. Irvin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from ctypes import Structure, Union, c_int, c_short
from dataclasses import dataclass

class _C_Cell(Structure):
    _fields_ = [
        ("z", c_short),
        ("x", c_short)
    ]

class _C_Interator(Union):
    _fields_ = [("iterator", c_int),
                ("cell", _C_Cell)]

@dataclass
class CellIteratorData:
    iterator: int = 0
    x: int = None
    z: int = None

    def __post_init__(self):
        cell = _C_Cell(self.z, self.x)
        self._c_iterator = _C_Interator()
        self._c_iterator.cell = cell
        self._c_iterator.iterator = self.iterator


__all__ = [
    "CellIteratorData"
]
