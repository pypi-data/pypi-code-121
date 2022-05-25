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

from PyCosmo._Tables import Tables
from PyCosmo.LinearPerturbationBase import LinearPerturbationBase


class LinearPerturbationTable(LinearPerturbationBase):

    """
    This class represents the interface to the tables class, which builds
    tabulated data for the costly calculations. Using this tabulated data
    this class constructs interpolation functions which can be called instead
    of the full function in order to increase speed.
    """

    # TODO: Tables -> Think about how to set the tolerance, adaptive?
    def __init__(self, lin_pert, pk_a_k_params=None):
        self._lin_pert = lin_pert
        self._tables = Tables()

        # TODO: Tables -> set the tolerance with enrich?
        self._enrich_params(pk_a_k_params)

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        """
        Returns an interpolated linear matter power spectrum computed from a predefined
        grid with interpolation error smaller than tol which has been set with
        enrich_params.
        :param: a: scale factor [1]
        :param: k: wavenumber [Mpc^-1]
        :return: P(k, a): interpolated matter power spectrum P(k) [Mpc^3]
        """

        if not hasattr(self, "pk_lin_interp_loga_logk"):
            self._setup_interpolation()

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)

        if diag_only:
            assert len(a) == len(k)

        # Add out-of-bounds behaviour to RectBivariateSpline
        loga = np.log10(a)
        logk = np.log10(k)

        limits = self.pk_a_k_params["limits"]
        outbounds = np.array(
            [
                np.any(loga < limits["xmin"]),
                np.any(loga > limits["xmax"]),
                np.any(logk < limits["ymin"]),
                np.any(logk > limits["ymax"]),
            ],
            dtype="bool",
        )

        queriedlims = np.hstack(
            [np.amin(loga), np.amax(loga), np.amin(logk), np.amax(logk)]
        )
        if np.any(outbounds):
            for i in range(len(outbounds)):
                if outbounds[i]:
                    # TODO: raise Exception here
                    print(
                        "Queried value exceeds %s"
                        % (self.pk_a_k_params["limits"].keys()[i])
                    )
                    print("Queried value = ", queriedlims[i])
                    print("Current limit = ", self.pk_a_k_params["limits"].values()[i])
            raise ValueError("interpolation out of bounds. Increase the range.")

        if diag_only:
            return self.pk_lin_interp_loga_logk.ev(np.log10(k), np.log10(a))
        else:
            return self.pk_lin_interp_loga_logk(np.log10(k), np.log10(a))

    def _setup_interpolation(self):
        # Calculate the grid and the function values on the grid
        (func_vals, a_grid, k_grid, __, __, __) = self._tables.interp_grid(
            self._lin_pert.powerspec_a_k, self.pk_a_k_params
        )
        self.pk_lin_interp_loga_logk = interpolate.RectBivariateSpline(
            np.log10(k_grid), np.log10(a_grid), func_vals
        )

    def growth_a(self, a=1.0, k=None, norm=0, verbose=False):
        """
        Returns an interpolated growth factor computed from a predefined grid with
        interpolation error smaller than tol which has been set with enrich_params.
        """

        print(
            "Interpolated growth factor is currently not supported, returning "
            "the exact growth factor instead."
        )

        return self._lin_pert.growth_a(a, k, norm)

    def transfer_k(self, k):
        """
        Returns an interpolated transfer function computed from a predefined grid
        with interpolation error smaller than tol which has been set with enrich_params.
        """

        print(
            "Interpolated transfer function is currently not supported, returning "
            "the exact transfer function instead."
        )

        return self._lin_pert.transfer_k(k)

    def _enrich_params(self, pk_a_k_params):
        """
        Sets the interpolation limits and the interpolation parameters for the
        linear matter power spectrum as a function of k and l.
        :param pk_a_k_params: dictionary containing the interpolation parameters for pk
                              as a function of k (or None)
        :return:
        """

        # TODO: currently commented out all default settings if we decide to go with
        # adaptive=True
        limit_keys = ("xmin", "xmax", "ymin", "ymax")
        calc_keys = ("dim", "gridtype", "nx", "ny", "adaptive", "tol")

        # Set up the limits for linear power spectrum in function of a and k
        if pk_a_k_params is None:
            # Set the default limits and accuracy parameters
            # amin = -3
            # amin = np.log10(5.0001e-2)
            lnamax = 0
            lnkmin = -4
            lnkmax = 5
            zmax = self._lin_pert.max_redshift([10**lnkmin, 10**lnkmax])
            lnamin = -np.log10(1 + zmax) * 0.99999  # account for rounding issues

            dim = 2
            gridtype = "log"
            nx = 600
            ny = 1000
            adaptive = False
            tol = 10**-3

            limits = dict(zip(limit_keys, (lnamin, lnamax, lnkmin, lnkmax)))
            calc = dict(zip(calc_keys, (dim, gridtype, nx, ny, adaptive, tol)))
        elif pk_a_k_params is not None:
            limits = {
                key: value for key, value in pk_a_k_params.items() if key in limit_keys
            }
            calc = {
                key: value for key, value in pk_a_k_params.items() if key in calc_keys
            }
        pk_a_k_params = {"limits": limits, "calc": calc}

        # Set up the limits for linear power spectrum in function of a and l
        self.pk_a_k_params = pk_a_k_params
