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
from collections import OrderedDict

import sympy as sp

from .globals import Globals
from .integral import IntegralFunctionWrapper


class Sp2CVisitor(object):
    def __init__(self, globals_=None):
        self.extra_wrappers = OrderedDict()
        if globals_ is None:
            globals_ = Globals()
        self.globals_ = globals_
        self.integral_count = 0

    def visit(self, expr):
        if hasattr(self, "visit_{0}".format(type(expr).__name__)):
            return getattr(self, "visit_{0}".format(type(expr).__name__))(expr)
        else:
            return self.generic_visit(expr)

    def generic_visit(self, expr):
        if hasattr(expr, "to_c"):
            return expr.to_c(self)
        raise Exception(
            "Not Implemented Expression: {0}: {1!s}".format(type(expr).__name__, expr)
        )

    def visit_Add(self, expr):
        return "({0})".format(" + ".join([self.visit(arg) for arg in expr.args]))

    def visit_Mul(self, expr):
        return " * ".join([self.visit(arg) for arg in expr.args])

    def visit_besselj(self, expr):
        order, arg = expr.args
        return "gsl_sf_bessel_Jn({0}, {1})".format(self.visit(order), self.visit(arg))

    def visit_besseli(self, expr):
        order, arg = expr.args
        return "gsl_sf_bessel_In({0}, {1})".format(self.visit(order), self.visit(arg))

    def visit_besselk(self, expr):
        order, arg = expr.args
        return "gsl_sf_bessel_Kn({0}, {1})".format(self.visit(order), self.visit(arg))

    def visit_bessely(self, expr):
        order, arg = expr.args
        return "gsl_sf_bessel_Yn({0}, {1})".format(self.visit(order), self.visit(arg))

    def visit_gamma(self, expr):
        arg = expr.args[0]
        return "gsl_sf_gamma({0})".format(self.visit(arg))

    def visit_Pow(self, expr):
        if isinstance(expr.exp, sp.numbers.Number):
            power = float(expr.exp)
            sign = -1 if power < 0 else 1

            if sign * expr.exp == 0.5:
                ret = "sqrtl({0})".format(self.visit(expr.base))
            elif sign * expr.exp == 1:
                ret = self.visit(expr.base)
            elif sign * expr.exp == 2:
                ret = "{0} * {0}".format(self.visit(expr.base))
            elif sign * expr.exp == 3:
                ret = "{0} * {0} * {0}".format(self.visit(expr.base))
            elif sign * expr.exp == 4:
                ret = "{0} * {0} * {0} * {0}".format(self.visit(expr.base))
            else:
                ret = "pow({0}, {1})".format(self.visit(expr.base), abs(power))
            return "1. / ({0})".format(ret) if sign < 0 else ret

        return "pow({0}, {1})".format(self.visit(expr.base), self.visit(expr.exp))

    def visit_Integer(self, expr):
        return str(expr.p)

    def visit_Abs(self, expr):
        return "fabs({})".format(self.visit(expr.args[0]))

    def visit_Rational(self, expr):
        return "{0} / {1}".format(float(expr.p), float(expr.q))

    def visit_Float(self, expr):
        return str(float(expr))

    def visit_Symbol(self, expr):
        return expr.name

    def visit_NegativeOne(self, expr):
        return "-1"

    def visit_Zero(self, expr):
        return "0"

    def visit_One(self, expr):
        return "1"

    def visit_Half(self, expr):
        return "0.5"

    def visit_float(self, expr):
        return str(expr)

    def visit_int(self, expr):
        return str(expr)

    def visit_sin(self, expr):
        return "sin({})".format(self.visit(expr.args[0]))

    def visit_cos(self, expr):
        return "cos({})".format(self.visit(expr.args[0]))

    def visit_log(self, expr):
        return "log({})".format(self.visit(expr.args[0]))

    def visit_exp(self, expr):
        return "exp({})".format(self.visit(expr.args[0]))

    def visit_tanh(self, expr):
        return "tanh({})".format(self.visit(expr.args[0]))

    def visit_Pi(self, expr):
        return "3.14159265358979323846"

    def visit_Infinity(self, expr):
        return "INFINITY"

    def visit_NegativeInfinity(self, expr):
        return "-INFINITY"

    def visit__Vector(self, expr):
        return str(expr)

    def visit_VectorElement(self, expr):
        return str(expr)

    def visit__Integral(self, integral):

        integrand, integration_variable, low, high, id_ = integral.args[:-1]

        # the variables for the integrand. we include the limits here
        # for nested integrals:

        free_variables_integrand = sorted(
            (integrand.free_symbols) - set(self.globals_.variables), key=str
        )

        variables_integrand = free_variables_integrand + [integration_variable]

        args = ["_arg_{}".format(i) for i in range(len(variables_integrand))]

        subs = {free_var: arg for (free_var, arg) in zip(variables_integrand, args)}

        integrand = integrand.subs(subs)

        key = compute_integral_fingerprint(
            integrand, integration_variable, low, high, id_, free_variables_integrand
        )

        integrand_name = "integrand___{}".format(key)
        integral_function_name = "integral___{}".format(key)

        if integral_function_name not in self.extra_wrappers:

            from .function import InternalFunction, function_wrapper_factory

            integrand_as_function = InternalFunction(
                integrand_name,
                integrand.expression,
                *args
                # *tuple(v.as_function_arg() for v in variables_integrand),
            )

            integrand_wrapper = function_wrapper_factory(
                integrand_as_function, self.globals_, self
            )
            integrand_wrapper.setup_code_generation()
            self.extra_wrappers[integrand_name] = integrand_wrapper

            # low_expression_in_c = self.visit(low)
            # high_expression_in_c = self.visit(high)

            integral_function_wrapper = IntegralFunctionWrapper(
                integral_function_name,
                args[
                    :-1
                ],  # tuple(v.as_function_arg() for v in free_variables_integrand),
                # low_expression_in_c,
                # high_expression_in_c,
                integrand_name,
                id_,
            )

            integral_function_wrapper.setup_code_generation()
            self.extra_wrappers[integral_function_name] = integral_function_wrapper

        low = self.visit(low)
        high = self.visit(high)
        call = "{}({})".format(
            integral_function_name,
            ", ".join(str(var) for var in free_variables_integrand + [low, high]),
        )
        return call

    def visit_Integrand(self, expr):
        return self.visit(expr.expression)

    def visit_IfThenElse(self, expr):
        cond, v1, v2 = expr.args
        return "(({}) ? ({}) : ({}))".format(
            self.visit(cond), self.visit(v1), self.visit(v2)
        )

    def visit_ERROR(self, expr):
        assert hasattr(expr, "message")
        assert isinstance(expr.message, str)
        return 'set_error_message("{}")'.format(expr.message)

    def visit_StrictLessThan(self, expr):
        return "(({}) < ({}))".format(
            self.visit(expr.args[0]), self.visit(expr.args[1])
        )

    def visit_LessThan(self, expr):
        return "(({}) <= ({}))".format(
            self.visit(expr.args[0]), self.visit(expr.args[1])
        )

    def visit_StrictGreaterThan(self, expr):
        return "(({}) > ({}))".format(
            self.visit(expr.args[0]), self.visit(expr.args[1])
        )

    def visit_GreaterThan(self, expr):
        return "(({}) >= ({}))".format(
            self.visit(expr.args[0]), self.visit(expr.args[1])
        )

    def visit_Equality(self, expr):
        return "(({}) == ({}))".format(
            self.visit(expr.args[0]), self.visit(expr.args[1])
        )

    def visit_Unequality(self, expr):
        return "(({}) != ({}))".format(
            self.visit(expr.args[0]), self.visit(expr.args[1])
        )

    def visit_InterpolationFunction1DInstance(self, expr):
        from .interpolation import InterpolationFunction1DWrapper

        self.extra_wrappers[expr._name] = InterpolationFunction1DWrapper(expr, self)
        return "(__ip_{}({}))".format(expr._name, self.visit(expr.argument))


def compute_integral_fingerprint(
    integrand, integration_variable, low, high, id_, free_variables_integrand
):

    integrand = integrand.subs({integration_variable: "__integration_variable"})
    key = hashlib.md5(
        (str(integrand) + str(id_)).encode("utf-8")  # + str(low) + str(high)
    ).hexdigest()
    return key
