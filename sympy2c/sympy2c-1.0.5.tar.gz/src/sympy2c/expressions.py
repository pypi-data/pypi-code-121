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


class Min(sp.Expr):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def free_symbols(self):
        return self.a.free_symbols | self.b.free_symbols

    def to_c(self, visitor):
        return "(_min({}, {}))".format(visitor.visit(self.a), visitor.visit(self.b))


class Max(Min):
    def to_c(self, visitor):
        return "(_max({}, {}))".format(visitor.visit(self.a), visitor.visit(self.b))


class isnan(sp.Expr):
    def __init__(self, a):
        self.a = a

    @property
    def free_symbols(self):
        return self.a.free_symbols

    def to_c(self, visitor):
        # from https://stackoverflow.com/questions/570669
        return "({0} != {0})".format(visitor.visit(self.a))


class hyper_2f1(sp.Expr):
    def __init__(self, a, b, c, x):
        self.a = a
        self.b = b
        self.c = c
        self.x = x

    @property
    def free_symbols(self):
        return (
            self.a.free_symbols
            | self.b.free_symbols
            | self.c.free_symbols
            | self.x.free_symbols
        )

    def to_c(self, visitor):
        # from https://stackoverflow.com/questions/570669
        return "(gsl_sf_hyperg_2F1({}, {}, {}, {}))".format(
            visitor.visit(self.a),
            visitor.visit(self.b),
            visitor.visit(self.c),
            visitor.visit(self.x),
        )
