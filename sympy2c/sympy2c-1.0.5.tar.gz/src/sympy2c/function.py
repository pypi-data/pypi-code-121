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

import sympy as sp
from sympy.core.containers import Tuple
from sympy.matrices.immutable import ImmutableDenseMatrix

from .utils import align, bound_symbols, concat_generator_results
from .vector import Vector, VectorElement
from .wrapper import WrapperBase

_hash_cache = {}


def expression_hash(e):
    return hashlib.md5(str(e.sort_key()).encode("utf-8")).digest()


def is_symbol_sublist(li1, li2):
    return " ".join(map(str, li1)) in " ".join(map(str, li2))


class Alias:
    def __init__(self, name, *symbols):
        assert isinstance(name, str)
        assert all(isinstance(symbol, sp.Symbol) for symbol in symbols)
        assert not name.startswith(
            "_"
        ), "you must not use underscore as first character"
        self.name = name
        self.symbols = symbols

    @property
    def as_vector(self):
        return Vector(self.name, len(self.symbols))

    def __str__(self):
        return "Alias({}={})".format(self.name, self.symbols)


class InternalFunction(sp.Function("Function", nargs=3, real=True)):
    def __new__(clz, name, expressions, *args):

        # fix after unpickling
        if len(args) == 1 and isinstance(args[0], Tuple):
            args = args[0]

        if not isinstance(expressions, (list, tuple)):
            expressions = [expressions]

        aliases = [a for a in args if isinstance(a, Alias)]
        args = [a.as_vector if isinstance(a, Alias) else a for a in args]

        instance = super().__new__(clz, name, sp.Matrix(expressions), tuple(args))

        instance.aliases = aliases
        instance._unique_id = None
        return instance

    def __getstate__(self):
        # we need default impl, else aliases handling will not work
        return self.__dict__

    def __setstate__(self, dd):
        # we need default impl, else aliases handling will not work
        self.__dict__.update(dd)

    def get_unique_id(self):
        if self._unique_id is None:
            md5 = hashlib.md5()
            md5.update(str(self._name).encode("utf-8"))
            for e in self.expressions:
                md5.update(expression_hash(e))
            md5.update(str(self.arguments).encode("utf-8"))
            self._unique_id = md5.hexdigest()
        return self._unique_id

    @property
    def free_symbols(self):
        return set(self.args[1].free_symbols) - set(self.args[1])

    @property
    def _name(self):
        return self.args[0]

    @property
    def expressions(self):
        return list(self.args[1])

    @property
    def arguments(self):
        return self.args[2]

    def __call__(self, *args):
        assert len(args) == len(self.arguments)
        return self.args[1].subs({in_: out for in_, out in zip(self.arguments, args)})


class Function(InternalFunction):
    pass


def _signature(expression, max_len=100):
    result = str(expression)
    if len(result) > max_len:
        result = result[: max_len - 3] + "..."
    return result


def function_wrapper_factory(function, globals_, visitor):
    expose_to_python = isinstance(function, Function)
    if len(function.expressions) == 1:
        return RealValuedFunctionWrapper(function, globals_, visitor, expose_to_python)
    else:
        return VectorValuedFunctionWrapper(
            function, globals_, visitor, expose_to_python
        )


class _FunctionWrapperBase(WrapperBase):
    def __init__(self, function, globals_, visitor, expose_to_python):
        assert set(function.arguments) & set(globals_.variables) == set(())
        self.name = function._name
        self.expressions = list(function.expressions)
        self.variables = function.arguments
        self.aliases = function.aliases

        self.function = function

        self.globals_ = globals_
        self.visitor = visitor
        self.expose_to_python = expose_to_python

    def determine_required_extra_wrappers(self):
        pass

    def setup_code_generation(self):
        self.in_variables = [
            var[0] if isinstance(var, tuple) else var for var in self.variables
        ]

        self.args = ", ".join(
            "double {}".format(var.c_args_decl()) for var in self.in_variables
        )

        self.cython_args = ", ".join(
            "{}".format(var.cython_decl()) for var in self.in_variables
        )

        self.ufunc_args = ", ".join(
            "double[{}] {}".format(":, :" if var.is_vector else ":", var._name())
            for var in self.in_variables
        )

        common_expressions, simplified_expressions = sp.cse(
            self.expressions, ignore=list(bound_symbols(*self.expressions))
        )

        # this visit calls can create integrand and integral functions which are avail
        # at self.visitor.extra_wrappers after self.visitor.visit finished:
        self.common_expressions = [
            (xi, self.visitor.visit(e)) for (xi, e) in common_expressions
        ]

        self.simplified_expressions = [
            self.visitor.visit(e) for e in simplified_expressions
        ]

    def get_unique_id(self):
        md5 = hashlib.md5()
        md5.update(self.function.get_unique_id().encode("utf-8"))
        md5.update(str(self.globals_.get_unique_id()).encode("utf-8"))
        return md5.hexdigest()


class MatrixValuedFunctionWrapper(_FunctionWrapperBase):
    def __init__(self, function, globals_, visitor, expose_to_python):
        assert set(function.arguments) & set(globals_.variables) == set(())
        _FunctionWrapperBase.__init__(
            self, function, globals_, visitor, expose_to_python
        )

        expression = function.args[1]
        assert isinstance(expression, ImmutableDenseMatrix)

        self.expressions = expression[:]

        self.variables = function.arguments
        self.globals_ = globals_

        self.m = expression.rows
        self.n = expression.cols

    def setup_code_generation(self):
        super().setup_code_generation()

        self._args = self.args

        if self.args:
            self.args = "{}, double _result[{}]".format(self.args, self.n * self.m)
        else:
            self.args = "double _result[{}]".format(self.n * self.m)

    @concat_generator_results
    def c_code(self, header_file_path):

        arrays_to_declare = set()
        scalars_to_declare = set()
        for alias in self.aliases:
            for symbol in alias.symbols:
                if isinstance(symbol, VectorElement):
                    arrays_to_declare.add(symbol.parent)
                else:
                    scalars_to_declare.add(symbol)

        declare_arrays = "\n|    ".join(
            "double {};".format(array) for array in arrays_to_declare
        )

        declare_scalars = "\n|    ".join(
            "double {};".format(atomic) for atomic in scalars_to_declare
        )

        _set_aliases = []

        for alias in self.aliases:
            for i, symbol in enumerate(alias.symbols):
                _set_aliases.append("{} = {}[{}];".format(symbol, alias.name, i))

        set_aliases = "\n|    ".join(_set_aliases)

        set_common_vars = "\n|    ".join(
            "double {} = {};".format(var, expr)
            for (var, expr) in self.common_expressions
        )

        set_results = "\n|    ".join(
            "_result[{}] = {};".format(i, expr)
            for (i, expr) in enumerate(self.simplified_expressions)
            if expr != "0"
        )

        sympy_expressions = "\n|    // ".join(str(e) for e in self.expressions)

        yield align(
            """
        |extern "C" void _{name}({args}) {{
        |    // {sympy_expressions}
        |    {declare_arrays}
        |    {declare_scalars}
        |    {set_aliases}
        |    {set_common_vars}
        |    {set_results}
        |}}
        """.format(
                name=self.name,
                args=self.args,
                sympy_expressions=sympy_expressions,
                declare_arrays=declare_arrays,
                declare_scalars=declare_scalars,
                set_aliases=set_aliases,
                set_results=set_results,
                set_common_vars=set_common_vars,
            )
        )

    @concat_generator_results
    def c_header(self):
        # we insert "_" at beginning of c functions to avoid clash with
        # cython functions:
        yield align(
            """
        |extern "C" void _{name}({args});
        """
        ).format(name=self.name, args=self.args)

    @concat_generator_results
    def cython_code(self, header_file_path):

        if not self.expose_to_python:
            return
        # we insert "_" at beginning of c functions to avoid clash with
        # cython functions:
        for code in self.cython_header(header_file_path):
            yield code
        for code in self.cython_function_wrapper():
            yield code
        for code in self.cython_ufunc_wrapper():
            yield code

    def cython_header(self, header_file_path):
        yield align(
            """
        |cdef extern from "{header_file_path}":
        |    double _{name}({args})
        """.lstrip().format(
                header_file_path=header_file_path, name=self.name, args=self.args
            )
        )

    def cython_function_wrapper(self):

        values = ", ".join(str(v.as_function_arg()) for v in self.in_variables)
        if values:
            c_args = values + ", &result[0]"
        else:
            c_args = "&result[0]"
        signature = _signature(self.expressions)
        yield align(
            """
        |def {name}({args}):
        |    cdef np.ndarray[np.double_t, ndim=1] result
        |    cdef const char * _error_message
        |    cdef const char * _warning_message
        |
        |    clear_last_error_message()
        |    clear_last_warning_message()
        |
        |    result = np.zeros(({n} * {m},), dtype=np.double)
        |    _{name}({c_args})
        |
        |    _warning_message = get_last_warning_message()
        |    if _warning_message[0] != 0:
        |        warnings.warn(str(_warning_message, encoding="utf-8"))
        |    _error_message = get_last_error_message()
        |    if _error_message[0] != 0:
        |          raise ArithmeticError(str(_error_message, encoding="utf-8") +
        |                " when evaluating {signature}"
        |                )
        |
        |    return result.reshape({m}, {n})
        """.lstrip().format(
                name=self.name,
                args=self.cython_args,
                c_args=c_args,
                signature=signature,
                m=self.m,
                n=self.n,
            )
        )

    def cython_ufunc_wrapper(self):
        yield align(
            """
            |def {name}_ufunc():
            |    raise RuntimeError("no ufunc created vector valued function {name}")
            |
            """
        ).format(name=self.name)


class VectorValuedFunctionWrapper(MatrixValuedFunctionWrapper):
    def __init__(self, function, globals_, visitor, expose_to_python):
        assert set(function.arguments) & set(globals_.variables) == set(())
        _FunctionWrapperBase.__init__(
            self, function, globals_, visitor, expose_to_python
        )

        self.n = len(self.expressions)

    def setup_code_generation(self):
        _FunctionWrapperBase.setup_code_generation(self)

        self._args = self.args
        if self.args:
            self.args = "{}, double _result[{}]".format(self.args, self.n)
        else:
            self.args = "double _result[{}]".format(self.n)

    def cython_function_wrapper(self):

        values = ", ".join(str(v.as_function_arg()) for v in self.in_variables)
        if values:
            c_args = values + ", &result[0]"
        else:
            c_args = "&result[0]"
        signature = _signature(self.expressions)
        yield align(
            """
        |def {name}({args}):
        |    cdef np.ndarray[np.double_t, ndim=1] result
        |    cdef const char * _error_message
        |    cdef const char * _warning_message
        |
        |    clear_last_error_message()
        |    clear_last_warning_message()
        |
        |    result = np.zeros(({n},), dtype=np.double)
        |    _{name}({c_args})
        |
        |    _warning_message = get_last_warning_message()
        |    if _warning_message[0] != 0:
        |        warnings.warn(str(_warning_message, encoding="utf-8"))
        |    _error_message = get_last_error_message()
        |    if _error_message[0] != 0:
        |          raise ArithmeticError(str(_error_message, encoding="utf-8") +
        |                " when evaluating {signature}"
        |                )
        |
        |    return result
        """.lstrip().format(
                name=self.name,
                args=self.cython_args,
                c_args=c_args,
                signature=signature,
                n=self.n,
            )
        )


class RealValuedFunctionWrapper(_FunctionWrapperBase):
    def setup_code_generation(self):
        super().setup_code_generation()
        self.c_expression = self.simplified_expressions[0]

    @concat_generator_results
    def c_code(self, header_file_path):
        arrays_to_declare = set()
        scalars_to_declare = set()

        for alias in self.aliases:
            for symbol in alias.symbols:
                if isinstance(symbol, VectorElement):
                    arrays_to_declare.add(symbol.parent)
                else:
                    scalars_to_declare.add(symbol)

        declare_arrays = "\n|    ".join(
            "double {};".format(array) for array in arrays_to_declare
        )

        declare_scalars = "\n|    ".join(
            "double {};".format(atomic) for atomic in scalars_to_declare
        )

        _set_aliases = []

        for alias in self.aliases:
            for i, symbol in enumerate(alias.symbols):
                _set_aliases.append("{} = {}[{}];".format(symbol, alias.name, i))

        set_aliases = "\n|    ".join(_set_aliases)

        set_common_vars = "\n|    ".join(
            "double {} = {};".format(var, expr)
            for (var, expr) in self.common_expressions
        )

        # we insert "_" at beginning of c functions to avoid clash with
        # created python wrappers:
        result = align(
            """
        |extern "C" double _{name}({args}) {{
        |    // {sympy_expression}
        |    {declare_arrays}
        |    {declare_scalars}
        |    {set_aliases}
        |    {set_common_vars}
        |    return {c_expression};
        |}}
        """.format(
                name=self.name,
                args=self.args,
                sympy_expression=self.expressions[0],
                declare_arrays=declare_arrays,
                declare_scalars=declare_scalars,
                set_aliases=set_aliases,
                set_common_vars=set_common_vars,
                c_expression=self.c_expression,
            )
        )
        yield result

    @concat_generator_results
    def c_header(self):
        # we insert "_" at beginning of c functions to avoid clash with
        # cython functions:
        yield align(
            """
        |extern "C" double _{name}({args});
        """
        ).format(name=self.name, args=self.args)

    @concat_generator_results
    def cython_code(self, header_file_path):
        # we insert "_" at beginning of c functions to avoid clash with
        # cython functions:
        if not self.expose_to_python:
            return

        for code in self.cython_header(header_file_path):
            yield code
        for code in self.cython_function_wrapper():
            yield code
        for code in self.cython_ufunc_wrapper():
            yield code

    def cython_header(self, header_file_path):
        yield align(
            """
        |cdef extern from "{header_file_path}":
        |    double _{name}({args})
        """.lstrip().format(
                header_file_path=header_file_path, name=self.name, args=self.args
            )
        )

    def cython_function_wrapper(self):

        values = ", ".join(str(v.as_function_arg()) for v in self.in_variables)
        _checks = []

        for alias in self.aliases:
            msg = "{} does not have length {}".format(alias.name, len(alias.symbols))
            _checks.append(
                "assert len({}) == {}, '{}'".format(alias.name, len(alias.symbols), msg)
            )

        checks = "\n|    ".join(_checks)

        signature = _signature(self.expressions[0])
        yield align(
            """
        |def {name}({args}):
        |    cdef double result
        |    cdef const char * _error_message
        |    cdef const char * _warning_message
        |
        |    clear_last_error_message()
        |    clear_last_warning_message()
        |
        |    {checks}
        |    result = _{name}({values})
        |
        |    _warning_message = get_last_warning_message()
        |    if _warning_message[0] != 0:
        |        warnings.warn(str(_warning_message, encoding="utf-8"))
        |    _error_message = get_last_error_message()
        |    if _error_message[0] != 0:
        |          raise ArithmeticError(str(_error_message, encoding="utf-8") +
        |                " when evaluating {signature}"
        |                )
        |
        |    return result
        """.lstrip().format(
                name=self.name,
                checks=checks,
                args=self.cython_args,
                values=values,
                signature=signature,
            )
        )

    def cython_ufunc_wrapper(self):

        out_dim = len(self.variables)
        if out_dim == 0:
            return

        sizes_check = (
            "|    if len(set(({},)) - set((1,))) > 1:\n"
            "|        raise ValueError('lengths must be one or agree.')"
        ).format(", ".join(f"{vi._name()}.shape[0]" for vi in self.in_variables))

        out_size_computation = ("|    cdef size_t out_size = max({}, 0)").format(
            ", ".join(f"{vi._name()}.shape[0]" for vi in self.in_variables)
        )

        values_decl = "\n|    ".join(
            "cdef double{} _v{}".format(
                "[:]" if self.in_variables[i].is_vector else "", i
            )
            for i in range(out_dim)
        )

        set_values = "\n|        ".join(
            f"_v{j} = {arg._name()}[0] if {arg}.shape[0] == 1 else {arg._name()}[i]"
            for (j, arg) in enumerate(self.in_variables)
        )

        values = ", ".join(
            f"&_v{j}[0]" if var.is_vector else f"_v{j}"
            for j, var in enumerate(self.in_variables)
        )

        signature = _signature(self.expressions[0])

        yield align(
            """
        |@cython.boundscheck(False)
        |@cython.wraparound(False)
        |def {name}_ufunc({ufunc_args}):
        |    cdef np.ndarray[np.double_t, ndim=1, cast=True] result
        |    cdef const char * _error_message
        |    cdef const char * _warning_message
        |    cdef size_t i
        {sizes_check}
        {out_size_computation}
        |    {values_decl}
        |    result = np.empty((out_size,), dtype=np.double)
        |    cdef double[:] result_view = result
        |    clear_last_warning_message()
        |    clear_last_error_message()
        |
        |    for i in range(out_size):
        |        {set_values}
        |        result_view[i] = _{name}({values})
        |
        |    _warning_message = get_last_warning_message()
        |    if _warning_message[0] != 0:
        |        warnings.warn(str(_warning_message, encoding="utf-8"))
        |
        |    _error_message = get_last_error_message()
        |    if _error_message[0] != 0:
        |          raise ArithmeticError(str(_error_message, encoding="utf-8") +
        |                " when evaluating {signature}"
        |                )
        |    return result
        """.lstrip().format(
                name=self.name,
                ufunc_args=self.ufunc_args,
                out_dim=out_dim,
                sizes_check=sizes_check,
                out_size_computation=out_size_computation,
                values_decl=values_decl,
                set_values=set_values,
                values=values,
                signature=signature,
            )
        )
