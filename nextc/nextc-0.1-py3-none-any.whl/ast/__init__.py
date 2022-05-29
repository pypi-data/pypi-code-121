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

from llvmlite import ir

from ..compile import core as ir_core


class Print:
    def __init__(self, ir_core: ir_core.Configurator, value):
        self.ir = ir_core
        self.value = value

    def eval(self):
        val = self.value.eval()

        voidptr_type = ir.IntType(8).as_pointer()
        fmt = '%i \n\0'
        c_fmt = ir.Constant(
            ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode('utf8'))
        )
        global_fmt = ir.GlobalVariable(self.ir.module, c_fmt.type, 'fstr')
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.ir.builder.bitcast(global_fmt, voidptr_type)

        self.ir.builder.call(self.ir._funcs.print, [fmt_arg, val])


class Integer:
    def __init__(self, ir_core: ir_core.Configurator, value: str):
        self.ir = ir_core
        self.value = value

    def eval(self):
        return ir.Constant(ir.IntType(len(self.value)), int(self.value))
