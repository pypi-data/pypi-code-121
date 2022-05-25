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

from .utils import align


def create_interface_onary():
    return align(
        """
        |class OneAryFunction {
        |
        |    public:
        |        virtual double operator()(double) = 0;
        |        virtual double operator()(double, void *) = 0;
        |};
        """
    )


def create_curry_class(n_fixed_args):
    """creates code to implement currying of a function.  Given a
    function with n_fixed_args + 1 double arguments, the first
    n_fixed_args are frozen, such that the resulting object behaves like
    a function with one input argument of type double"""

    class_name = "Curry_{}".format(n_fixed_args)

    function_args_decl = ", ".join("double" for i in range(n_fixed_args + 1))

    default_args_decl = "\n    ".join(
        "double _v{i};".format(i=i) for i in range(n_fixed_args)
    )

    cons_args_decl = ", ".join(
        [
            "double (*f)({function_args_decl})".format(
                function_args_decl=function_args_decl
            )
        ]
        + ["double v{i}".format(i=i) for i in range(n_fixed_args)]
    )

    attributes_init = ", ".join(
        ["_f(f)"] + ["_v{i}(v{i})".format(i=i) for i in range(n_fixed_args)]
    )

    fixed_args = ", ".join(["_v{i}".format(i=i) for i in range(n_fixed_args)] + ["x"])

    code = align(
        """
        |class {class_name}: public OneAryFunction {{
        |
        |      double (*_f)({function_args_decl});
        |      {default_args_decl}
        |
        |      public:
        |           {class_name}({cons_args_decl}): {attributes_init} {{}};
        |
        |      double operator()(double x) {{
        |           return _f({fixed_args});
        |      }}
        |
        |      // for use as a gsl_function:
        |      double operator()(double x, void *) {{
        |           return _f({fixed_args});
        |      }}
        |}};"""
    ).format(
        class_name=class_name,
        function_args_decl=function_args_decl,
        default_args_decl=default_args_decl,
        cons_args_decl=cons_args_decl,
        attributes_init=attributes_init,
        fixed_args=fixed_args,
    )

    return class_name, code
