# Copyright 2022 VincentRPS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

from llvmlite import binding, ir

from .declarations import Delarator


class Configurator:
    def __init__(self):
        self.binding = binding
        self.binding.initialize()
        self.binding.initialize_native_target()
        self.binding.initialize_native_asmprinter()
        self._initiate_execution_engine()
        self.module = ir.Module(name=__file__)
        self.module.triple = self.binding.get_default_triple()
        _fn_t = ir.FunctionType(ir.VoidType(), [], False)
        main_fn = ir.Function(self.module, _fn_t, 'main')
        block = main_fn.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)
        self._funcs = Delarator(self.module, self.binding)

    def _initiate_execution_engine(self):
        t = self.binding.Target.from_default_triple()
        t_machine = t.create_target_machine()
        backing_mod = binding.parse_assembly('')
        engine = binding.create_mcjit_compiler(backing_mod, target_machine=t_machine)
        self._engine = engine

    def compile_(self) -> binding.ModuleRef:
        self.builder.ret_void()
        _ir = str(self.module)
        mod = self.binding.parse_assembly(_ir)
        try:
            mod.verify()
        except RuntimeError:
            raise

        self._engine.add_module(mod)
        self._engine.finalize_object()
        self._engine.run_static_constructors()
        return mod

    def create_output(self, fp: str):
        try:
            with open(file=fp, mode='x') as _fp:
                self.compile_()
                _fp.write(str(self.module))
        except FileExistsError:
            os.unlink(fp)
            self.create_output(fp)
        except FileNotFoundError:
            dir = fp.split('/')[0]
            os.makedirs(dir)
            self.create_output(fp)
