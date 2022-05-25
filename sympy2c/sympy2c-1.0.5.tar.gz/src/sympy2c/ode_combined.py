# This file is part of sympy2c.
#
# Copyright (C) 2013-2022 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import os
from hashlib import md5
from textwrap import dedent, indent

from .ode_fast import OdeFast, concat_generator_results

CYTHON_TEMPLATE = "ode_combined_cython_template.pyx"


class OdeCombined:
    def __init__(self, name, ode_0, ode_1, switch_time, switch, merge):
        assert isinstance(ode_0, OdeFast), "only works for fast ode"
        assert isinstance(ode_1, OdeFast), "only works for fast ode"
        self.name = name
        self.odes = [ode_0, ode_1]
        self._unique_id = None

        self.switch_time_function_src = indent(
            dedent(inspect.getsource(switch_time)), "    "
        )
        self.switch_function_src = indent(dedent(inspect.getsource(switch)), "    ")
        self.merge_function_src = indent(dedent(inspect.getsource(merge)), "    ")

        self.switch_time_function_name = switch_time.__name__
        self.switch_function_name = switch.__name__
        self.merge_function_name = merge.__name__

    def __str__(self):
        return "<OdeCombined {}, {}, {}, {}, {}>".format(
            self.name, self.odes, self.switch_time, self.switch, self.merge
        )

    @property
    def wrapper(self):
        return OdeCombinedWrapper

    def get_unique_id(self):
        if self._unique_id is None:
            hasher = md5()
            hasher.update(self.name.encode("utf-8"))
            for ode in self.odes:
                hasher.update(ode.get_unique_id().encode("utf-8"))
            hasher.update(self.switch_time_function_src.encode("utf-8"))
            hasher.update(self.switch_function_src.encode("utf-8"))
            hasher.update(self.merge_function_src.encode("utf-8"))
            hasher.update(self.switch_time_function_name.encode("utf-8"))
            hasher.update(self.switch_function_name.encode("utf-8"))
            hasher.update(self.merge_function_name.encode("utf-8"))
            self._unique_id = hasher.hexdigest()
        return self._unique_id


class OdeCombinedWrapper:
    def __init__(self, ode_combined, globals_, visitor):
        self.ode_combined = ode_combined
        self.odes = ode_combined.odes
        self.globals_ = globals_
        self.visitor = visitor
        self.name = ode_combined.name
        self._unique_id = None

    def setup_code_generation(self):
        pass

    def get_unique_id(self):
        if self._unique_id is None:
            hasher = md5()
            hasher.update(self.ode_combined.get_unique_id().encode("utf-8"))
            # for level, level_traces in sorted(self.traces.items()):
            #    hasher.update(str(sorted(level_traces)).encode("utf-8"))
            self._unique_id = hasher.hexdigest()
        return self._unique_id

    def determine_required_extra_wrappers(self):
        return
        for ode in self.odes:
            for rhs in ode.rhs:
                self.visitor.visit(rhs)

    @concat_generator_results
    def c_header(self):
        yield f"PT get_new_traces_{self.name}();"

    @concat_generator_results
    def c_code(self, header_file_path):
        yield f"PT _new_traces_{self.name};"

    @concat_generator_results
    def cython_code(self, header_file_path):
        here = os.path.dirname(__file__)
        template = open(os.path.join(here, CYTHON_TEMPLATE)).read()

        symbols = repr(list(map(repr, self.odes[0].lhs)))

        yield template.format(
            id_=self.name,
            symbols=symbols,
            solver_0="solve_fast_{}".format(self.odes[0].name),
            solver_1="solve_fast_{}".format(self.odes[1].name),
            switch_time_function_src=self.ode_combined.switch_time_function_src,
            switch_function_src=self.ode_combined.switch_function_src,
            merge_function_src=self.ode_combined.merge_function_src,
            switch_time_function_name=self.ode_combined.switch_time_function_name,
            switch_function_name=self.ode_combined.switch_function_name,
            merge_function_name=self.ode_combined.merge_function_name,
        )
