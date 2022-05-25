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
from scipy import interpolate

COSMO_PARAMS = ["h", "omega_m", "omega_b", "omega_l", "w0", "wa", "n", "pk_norm"]

try:
    from pytimer import Timer

except ImportError:

    def Timer(*a, **kw):
        def dont_decorate(fun):
            return fun

        return dont_decorate


class Spline:
    def __init__(self, x, y):
        self.x_min = min(x)
        self.x_max = max(x)
        self.spline = interpolate.InterpolatedUnivariateSpline(x, y)

    def __call__(self, x):
        return self.spline(x)
        if isinstance(x, float):
            if x < self.x_min or x > self.x_max:
                return np.nan
            return self.spline(x)

        valid = (self.x_min <= x) * (x <= self.x_max)
        result = np.nan * np.ones_like(x)
        result[valid] = self.spline(x[valid])
        return result


class TheoryPredTables(object):
    """
    Class for calculation of tabulated cosmological quantities from PyCosmo.
    """

    def __init__(self, lin_pert):

        self._lin_pert = lin_pert
        self.pk_interp_loga_logk = None

    @Timer(average=True)
    def powerspec_tab_a_k(self, a=1.0, k=0.1, fields=None):
        # type: (object, object, object) -> object
        """
        Returns the interpolated linear matter power spectrum from PyCosmo.
        :param a: array of scale factor values a
        :param k: array of wave vector k values
        :return pk_lin_interp: interpolated linear power spectrum at a and k
        """

        k = np.atleast_1d(k)
        a = np.atleast_1d(a)

        if self.pk_interp_loga_logk is None:
            a_limit = 1 / (1 + self._lin_pert.max_redshift(k))

            print("Calculating the linear matter power spectrum...")
            a_temp = 10 ** np.linspace(-4, 0, 1000)
            a_temp = a_temp[a_temp >= a_limit]
            k_temp = 10 ** np.linspace(-5, 4, 1000)

            pk = self._lin_pert.powerspec_a_k(a=a_temp, k=k_temp)

            self.pk_interp_loga_logk = interpolate.RectBivariateSpline(
                np.log(k_temp), np.log(a_temp), pk
            )

        # interpolation only works if coordinates are sorted
        k_perm = np.argsort(k)
        a_perm = np.argsort(a)

        def invert(perm):
            result = np.zeros_like(perm)
            result[perm] = np.arange(len(perm))
            return result

        inv_k_perm = invert(k_perm)
        inv_a_perm = invert(a_perm)

        a = a[a_perm]
        k = k[k_perm]

        # Vetorise the interpolated function
        pk_lin_interp = self.pk_interp_loga_logk(np.log(k), np.log(a), grid=1)

        # bring result in right order:
        return pk_lin_interp[inv_k_perm, :][:, inv_a_perm]

    @Timer(average=True)
    def growth_tab_a(self, a=1.0):
        """
        Returns the interpolated growth factor from PyCosmo.
        :param a: array of scale factor values a
        :return growth_interp: interpolated growth factor at a
        """

        # Initialise the grid
        if not hasattr(self, "growth_interp_a"):
            print("Calculating the growth factor...")
            a_limit = 1 / (1 + self._lin_pert.max_redshift(1.0))
            a_temp = np.logspace(-4, 0, 500)
            a_temp = a_temp[a_temp >= a_limit]
            growth_temp = self._lin_pert.growth_a(a=a_temp)

            self.growth_interp_a = Spline(a_temp, growth_temp)

        growth_interp = self.growth_interp_a(a)

        return growth_interp

    @Timer(average=True)
    def inv_growth_tab_a(self, g=1.0):
        """
        Returns the interpolated inverse of the growth factor from PyCosmo.
        :param g: array of growth factor values g
        :return inv_growth_interp: interpolated inverse growth factor at g
        """

        # Initialise the grid
        if not hasattr(self, "inv_growth_interp_a"):
            print("Calculating the inverse growth factor...")
            a_temp = np.logspace(-4, 0, 500)
            a_limit = 1 / (1 + self._lin_pert.max_redshift(1.0))
            a_temp = a_temp[a_temp >= a_limit]
            growth_temp = self._lin_pert.growth_a(a=a_temp)

            self.inv_growth_interp_a = Spline(growth_temp, a_temp)

        inv_growth_interp = self.inv_growth_interp_a(g)

        return inv_growth_interp

    @Timer(average=True)
    def growth_suba(self, a=1.0):
        """
        Returns the growth factor divided by the scale factor a
        :param a: scale factor a
        :return growth_suba_temp: growth factor divided by scale factor
        """

        growth_suba_temp = self._lin_pert.growth_a(a=a) / a

        return growth_suba_temp

    @Timer(average=True)
    def growth_suba_deriv(self, a=1.0):
        """
        Returns the derivative of growth_suba by redshift z
        :param a: scale factor a
        :return growth_deriv: derivative of growth_suba w.r.t. z
        """

        delta = a * 10**-4

        growth_min2del = self.growth_suba(a=a - 2 * delta)
        growth_min1del = self.growth_suba(a=a - delta)
        growth_plus1del = self.growth_suba(a=a + delta)
        growth_plus2del = self.growth_suba(a=a + 2 * delta)

        growth_deriv = (
            1.0
            / (12.0 * delta)
            * (
                growth_min2del
                - 8.0 * growth_min1del
                + 8.0 * growth_plus1del
                - growth_plus2del
            )
        )

        # To transform from derivative w.r.t. a to z
        growth_deriv *= (-1) * a**2

        return growth_deriv

    @Timer(average=True)
    def growth_deriv(self, a=1.0, mode="fivepoint"):
        """
        Returns the derivative of the growth function w.r.t. a.
        :param a: scale factor
        :param mode: 5-point derivative or 2-point derivative
        :return growth_deriv: derivative of the growth factor w.r.t. a
        """
        delta = a * 10**-4

        growth_min2del = self._lin_pert.growth_a(a=a - 2 * delta)
        growth_min1del = self._lin_pert.growth_a(a=a - delta)
        growth_plus1del = self._lin_pert.growth_a(a=a + delta)
        growth_plus2del = self._lin_pert.growth_a(a=a + 2 * delta)

        growth_derivative = (
            1.0
            / (12.0 * delta)
            * (
                growth_min2del
                - 8.0 * growth_min1del
                + 8.0 * growth_plus1del
                - growth_plus2del
            )
        )
        if mode == "fivepoint":
            growth_derivative = (
                1.0
                / (12.0 * delta)
                * (
                    growth_min2del
                    - 8.0 * growth_min1del
                    + 8.0 * growth_plus1del
                    - growth_plus2del
                )
            )
        elif mode == "twopoint":
            growth_derivative = 1.0 / (2.0 * delta) * (growth_plus1del - growth_min1del)

        return growth_derivative
