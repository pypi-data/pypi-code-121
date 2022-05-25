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

import sympy as sp

from .symbol import Symbol
from .utils import align


class VectorElement(sp.Symbol):
    def __new__(cls, name, index=None):
        # index is not defined in base classes __new__ and as such  not provided when
        # unpickling, so we need default value to make unpickling work. when we unpickle
        # name is already of formm "v[i]".
        if index is not None:
            return super().__new__(cls, "{}[{}]".format(name, index))
        else:
            return super().__new__(cls, name)

    def c_args_decl(self):
        return self

    def __str__(self):
        return self.name

    def _shrinked(self):
        # name + index without the brackets. a[0] -> a0
        return self.name.replace("[", "").replace("]", "")

    @property
    def index(self):
        ix_part = self.name.split("[")[1][:-1]
        return int(ix_part)

    @property
    def vector_name(self):
        return self.name.split("[")[0]

    def as_function_arg(self):
        return Symbol(self._shrinked())

    def cython_decl(self):
        return "double " + self._shrinked()

    @property
    def free_symbols(self):
        return set((self,))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.name == other.name

    def __getstate__(self):
        return sp.Symbol.__getstate__(self), self.parent

    def __setstate__(self, data):
        state, self.parent = data
        sp.Symbol.__setstate__(self, state)


class Vector(sp.Symbol):
    def __new__(cls, name, size=None):
        # size is not defined in base classes __new__ and as such  not provided when
        # unpickling, so we need default value to make unpickling work. when we unpickle
        # name is already of formm "v[i]".
        assert not name.startswith(
            "_"
        ), "you must not use underscore as first character"

        if size is not None:
            return super().__new__(cls, "{}[{}]".format(name, size))
        else:
            return super().__new__(cls, name)

    is_vector = True

    def __str__(self):
        return self.name

    def _name(self):
        return self.name.split("[")[0]

    def _size(self):
        number = self.name.split("[")[1].lstrip("[").rstrip("]")
        return int(number)

    __len__ = _size

    def c_args_decl(self):
        return self.name

    def __getitem__(self, i):
        if not 0 <= i < self._size():
            raise IndexError()
        result = VectorElement(self._name(), i)
        result.parent = self
        return result

    def as_function_arg(self):
        return "&{}[0]".format(self._name())

    def cython_decl(self):
        return "double [::1] {}".format(self._name())

    @property
    def free_symbols(self):
        elements = (VectorElement(self._name(), i) for i in range(self._size()))
        return set(elements)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.name == other.name

    def setter_c_code(self):
        return align(
            """
            |extern "C" void _set_{_name}(double *_v) {{
            |    memcpy({_name}, _v, {n} * sizeof(double));
            |}}
            """
        ).format(_name=self._name(), n=self._size())

    def getter_c_code(self):
        return align(
            """
            |extern "C" void _get_{_name}(double *result) {{
            |    memcpy(result, {_name}, {n} * sizeof(double));
            |}}
            """
        ).format(_name=self._name(), n=self._size())

    def setter_header_code(self):
        return "void _set_{_name}(double *); ".format(_name=self._name())

    def getter_header_code(self):
        return "void _get_{_name}(double *); ".format(_name=self._name())

    setter_cython_header_code = setter_header_code
    getter_cython_header_code = getter_header_code

    def cython_globals_setter_code(self):
        return (
            align(
                """
           |if "{_name}" in _g:
           |    values_1d = np.array(_g["{_name}"], dtype=np.double, order="c")
           |    if values_1d.shape[0] != {n}:
           |         raise ValueError("value must be list of 1d array of length {n}")
           |    _set_{_name}(&values_1d[0])
           """
            )
            .format(_name=self._name(), n=self._size())
            .rstrip()
        )

    def cython_globals_getter_code(self):
        return align(
            """
           |values_1d = np.zeros(({n},), dtype=np.double)
           |_get_{_name}(&values_1d[0])
           |result["{_name}"] = np.array(values_1d)
           """
        ).format(_name=self._name(), n=self._size())
