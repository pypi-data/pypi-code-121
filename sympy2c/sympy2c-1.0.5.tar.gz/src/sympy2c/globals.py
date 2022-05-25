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

import hashlib
import pickle

from .utils import align, concat_generator_results


class Globals(object):
    def __init__(self, *variables):
        self.variables = set(variables)

    def add_variable(self, symbol):
        assert symbol not in self.variables, "variable was already set as being global"
        self.variables.add(symbol)

    def get_unique_id(self):
        data = sorted(map(str, self.variables))
        return hashlib.md5(pickle.dumps(data)).hexdigest()

    def __iter__(self):
        return iter(self.variables)

    @concat_generator_results
    def c_code(self, header_file_path):
        for variable in self.variables:
            yield "static double {};".format(variable.c_args_decl())

        yield ""
        for variable in self.variables:
            yield variable.setter_c_code()
            yield variable.getter_c_code()
        yield ""

    @concat_generator_results
    def c_header(self):
        yield """extern "C" { """
        for variable in self.variables:
            yield "    " + variable.setter_header_code()
            yield "    " + variable.getter_header_code()
        yield "}"
        yield ""

    @concat_generator_results
    def cython_code(self, header_file_path):
        if self.variables:
            yield """cdef extern from "{header_file_path}": """.format(
                header_file_path=header_file_path
            )

            for variable in self.variables:
                yield "    " + variable.setter_cython_header_code()
                yield "    " + variable.getter_cython_header_code()
            yield ""

        yield "def set_globals(**_g):"

        if self.variables:
            yield "    cdef np.ndarray[np.double_t, ndim=1] values_1d"
            for variable in self.variables:
                for line in variable.cython_globals_setter_code().split("\n"):
                    yield "    " + line

        else:
            yield "    pass"

        yield align(
            r"""
                |class _Globals:
                |    def __setattr__(self, name, value):
                |        set_globals(**{name: value})
                |    def __getattr__(self, name):
                |        return get_globals()[name]
                |    def __str__(self):
                |        lines = []
                |        max_length = max(len(k) for k in get_globals().keys())
                |        for (key, value) in sorted(get_globals().items()):
                |            lines.append(
                |                 "{} = {}".format(key.ljust(max_length, " "), value)
                |            )
                |        return "\n".join(lines)
                |    def __getstate__(self):
                |        return None
                |    def __setstate__(self, data):
                |        pass
                |globals = _Globals()
                """
        )

        yield ""

        yield "def get_globals():"
        yield "    cdef np.ndarray[np.double_t, ndim=1] values_1d"
        yield "    result = {}"

        for variable in self.variables or []:
            for line in variable.cython_globals_getter_code().split("\n"):
                yield "    " + line
        yield "    return result"
        yield ""
