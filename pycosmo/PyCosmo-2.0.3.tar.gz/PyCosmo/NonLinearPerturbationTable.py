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
from PyCosmo.PerturbationBase import NonLinearPerturbationBase


class NonLinearPerturbationTable(NonLinearPerturbationBase):

    """
    This class represents the interface to the tables class, which builds
    tabulated data for the costly calculations. Using this tabulated data
    this class constructs interpolation functions which can be called instead
    of the full function in order to increase speed.
    """

    # TODO: Tables -> Think about how to set the tolerance, adaptive?
    def __init__(self, nonlin_pert, params):
        self._nonlin_pert = nonlin_pert
        self._tables = Tables()
        self.params = params
        # TODO: Tables -> set the tolerance with enrich?
        self._enrich_params()
        self.pk_nonlin_interp_loga_logk = None
        self.pk_nonlin_grid = None

    def k_nl(self, a=1.0):
        """
        Returns an interpolated non-linear wave number computed from a predefined grid
        with interpolation error smaller than tol which has been set with enrich_params.
        """

        print(
            "Interpolated non-linear wave number is currently not supported, returning "
            "the exact non-linear wave number instead."
        )

        return self._nonlin_pert.k_nl(a=a)

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        """
        Returns an interpolated nonlinear matter power spectrum computed from a
        predefined grid with interpolation error smaller than tol which has been set
        with enrich_params.
        :param: a: scale factor [1]
        :param: k: wavenumber [Mpc^-1]
        :return: P(k, a): interpolated nonlinear matter power spectrum P(k) [Mpc^3]
        """

        if self.pk_nonlin_interp_loga_logk is None:
            self._setup_nonlin_interp_loga_logk()

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)

        if diag_only:
            assert len(a) == len(k)

        # Add out-of-bounds behaviour to RectBivariateSpline
        loga = np.log10(a)
        logk = np.log10(k)
        limits = self._interpolation_params["limits"]
        outbounds = np.array(
            [
                np.any(loga < limits["xmin"]),
                np.any(loga > limits["xmax"]),
                np.any(logk < limits["ymin"]),
                np.any(logk > limits["ymax"]),
            ],
            dtype="bool",
        )

        axes = ("xmin", "xmax", "ymin", "ymax")
        queriedlims = np.hstack(
            [np.amin(loga), np.amax(loga), np.amin(logk), np.amax(logk)]
        )

        if np.any(outbounds):
            messages = []
            for i in range(len(outbounds)):
                if outbounds[i]:
                    axis = axes[i]
                    limit = self._interpolation_params["limits"][axis]
                    msg = "queried value {} exceeds {} limit {}".format(
                        queriedlims[i], axis, limit
                    )
                    messages.append(msg)
            raise ValueError("\n".join(messages))

        if diag_only:
            return self.pk_nonlin_interp_loga_logk.ev(logk, loga)
        else:
            return self.pk_nonlin_interp_loga_logk(logk, loga)

    def _setup_nonlin_interp_loga_logk(self):
        (func_vals, a_grid, k_grid, __, __, __) = self._tables.interp_grid(
            self._nonlin_pert.powerspec_a_k, self._interpolation_params
        )
        # Do the interpolation for the a values where pk is not nan. Otherwise the
        # interpolation breaks
        mask = np.isnan(func_vals)

        # extend mask: if there is a nan in a given colum, extend the mask to the full
        #              column
        mask_columnwise_or = np.any(mask, axis=0)
        mask[:, np.nonzero(mask_columnwise_or)[0]] = True

        func_vals = func_vals[~mask]
        # the previous operation flattened func_vals, so we reshape now:
        func_vals = func_vals.reshape(len(k_grid), -1)
        a_grid = a_grid[~mask_columnwise_or]

        if len(a_grid) < 2:
            raise ValueError(
                "could not setup interpolation table, to many nan values for "
                "given a range."
            )

        self.pk_nonlin_interp_loga_logk = interpolate.RectBivariateSpline(
            np.log10(k_grid), np.log10(a_grid), func_vals
        )

    def _enrich_params(self):
        """
        Sets the interpolation limits and the interpolation parameters for the
        nonlinear matter power spectrum as a function of k and l.

        :param _interpolation_params: dictionary containing the interpolation parameters
                                      for pk nonlin as a function of k (or None)
        :return: None
        """

        # Set the default limits and accuracy parameters
        lnkmin, lnkmax = -4, 5
        zmax = self._nonlin_pert.max_redshift([10**lnkmin, 10**lnkmax])
        lnamin = -np.log10(1 + zmax) * 0.99999  # account for rounding issues
        lnamax = 0

        limits = dict(xmin=lnamin, xmax=lnamax, ymin=lnkmin, ymax=lnkmax)

        agridsize = getattr(self.params, "a_size", 800)
        kgridsize = getattr(self.params, "k_size", 800)
        calc = dict(
            dim=2, gridtype="log", nx=agridsize, ny=kgridsize, adaptive=False, tol=1e-3
        )

        self._interpolation_params = {"limits": limits, "calc": calc}
