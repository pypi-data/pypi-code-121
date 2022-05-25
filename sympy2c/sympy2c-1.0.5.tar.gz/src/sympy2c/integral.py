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

from hashlib import md5

import sympy as sp
from sympy.matrices.matrices import MatrixBase

from .create_curry_class import create_curry_class
from .utils import align, concat_generator_results
from .wrapper import WrapperBase


def Integral(integrand, integration_variable, low, high, id_="default"):
    if "[" in str(integration_variable):
        raise ValueError("dont use array or array elements as integration variable")
    if not isinstance(low, (int, float)):
        assert integration_variable not in low.free_symbols

    if not isinstance(high, (int, float)):
        assert integration_variable not in high.free_symbols

    if isinstance(integrand, MatrixBase):
        integrands = list(integrand)
        assert len(integrands) == 1, "no implementation for vector valued integrals"
        integrand = integrands[0]

    if isinstance(low, (int, float)):
        low = sp.Number(low)
    if isinstance(high, (int, float)):
        high = sp.Number(high)

    integrand = Integrand(integrand, integration_variable)

    unique_id = md5(
        (
            str(integrand.sort_key() + low.sort_key() + high.sort_key())
            + str(integration_variable)
            + str(id_)
        ).encode("utf-8")
    ).hexdigest()

    # all args must be "sympy"-fiable:
    result = _Integral(
        integrand, integration_variable, low, high, id_, sp.Symbol(unique_id)
    )
    return result


class _Integral(sp.Function("Integral", nargs=6, real=True)):
    @property
    def free_symbols(self):
        integrand, integration_variable, low, high, id_ = self.args[:-1]
        return integrand.free_symbols | low.free_symbols | high.free_symbols

    def get_unique_id(self):
        return self.args[-1]

    def atoms(self, what=None):
        return (
            self.integrand.atoms(what)
            | self.low.atoms(what)
            | self.high.atoms(what)
            | self.integration_variable.atoms(what)
        )

    @property
    def integrand(self):
        return self.args[0]

    @property
    def integration_variable(self):
        return self.args[1]

    @property
    def low(self):
        return self.args[2]

    @property
    def high(self):
        return self.args[3]


class Integrand(sp.Expr):
    def __init__(self, expression, integration_variable):
        self.expression = expression
        self.integration_variable = integration_variable

    @property
    def free_symbols(self):
        return self.expression.free_symbols - {self.integration_variable}

    def atoms(self, what=None):
        return self.expression.atoms(what) | self.integration_variable.atoms(what)


IfThenElse = sp.Function("IfThenElse", nargs=3, real=True)


class ERROR(sp.Expr):
    def __new__(clz, message=None):
        # default value None required for unpickling!
        # we can not implement __init__ because sympy does some magick which
        # avoids setting new attributes within __init__
        instance = super().__new__(clz)
        instance.message = message
        return instance

    def __str__(self):
        return 'ERROR("{}")'.format(self.message)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dd):
        self.__dict__.update(dd)


def Checked(expr, message):
    return IfThenElse(expr, expr.lhs, ERROR(message))


class IntegralFunctionWrapper(WrapperBase):
    seen = set()

    @classmethod
    def reset(clz):
        clz.seen = set()

    def __init__(self, name, free_vars, integrand_name, id_):
        self.name = name
        self.free_vars = free_vars
        # self.low = low
        # self.high = high
        self.integrand_name = integrand_name
        self.id_ = id_

    def setup_code_generation(self):
        pass

    def c_header(self):
        args = ", ".join(
            "double {}".format(var) for var in self.free_vars + ["_low", "_high"]
        )

        return "double {name}({args});".format(name=self.name, args=args)

    def cython_code(self, header_file_path):
        return ""

    @concat_generator_results
    def c_code(self, header_file_path):

        curry_class_name, curry_class_code = create_curry_class(len(self.free_vars))

        # don't craeate same currying abstract base class multiple
        # times:
        if curry_class_name not in self.seen:
            self.seen.add(curry_class_name)
            yield curry_class_code

        args = ", ".join(
            "double {}".format(var) for var in self.free_vars + ["_low", "_high"]
        )

        # we insert "_" at beginning of c functions to avoid clash with
        # cython functions:
        cons_args = ", ".join(
            ["_" + self.integrand_name] + list(map(str, self.free_vars))
        )

        yield align(
            """
        |inline double {name}({args}) {{
        |    {curry_class_name} curried_function({cons_args});
        |    return quadpack_integration(&curried_function, "{id_}", _low, _high);
        |}}
        |"""
        ).format(
            name=self.name,
            id_=self.id_,
            # low=self.low,
            # high=self.high,
            args=args,
            curry_class_name=curry_class_name,
            cons_args=cons_args,
        )

    def determine_required_extra_wrappers(self):
        pass
