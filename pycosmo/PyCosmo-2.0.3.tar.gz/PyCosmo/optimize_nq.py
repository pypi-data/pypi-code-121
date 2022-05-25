# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
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

import numpy as np
import sympy as sp
from sympy.integrals import quadrature
from scipy.special import zeta


def gl_quadrature(mnu_relerr):
    def f(q):
        return 1 / (sp.exp(q) + 1)

    def test_fun(q):
        """
        test function used to determine the q sampling,
        massive neutrinos integrals should take similar form
        """
        iq = (
            sp.Pow(q, sp.Integer(2)) * f(q)
            + sp.Pow(q, sp.Integer(3)) * f(q)
            + sp.Pow(q, sp.Integer(4)) * f(q)
        )
        return iq

    q = sp.Symbol("q")
    value = (
        3 * zeta(3) / 2 + 7 * np.pi**4 / 120 + 45 * zeta(5) / 2
    )  # analytical result of test_fun integration

    nq = 5
    current_re = 1
    while current_re > mnu_relerr:
        """
        change quadrature until desired accuracy is reached
        """
        qq, weights = quadrature.gauss_laguerre(nq, nq + 3)
        result = sum(
            weights[i] * sp.exp(q).subs({q: qq[i]}) * test_fun(q).subs({q: qq[i]})
            for i in range(len(qq))
        )
        current_re = abs((result - value) / value)
        nq += 1
        if nq > 1000:
            raise ValueError(
                "the chosen value {} for mnu_relerr is too small".format(mnu_relerr)
            )
    return qq, weights
