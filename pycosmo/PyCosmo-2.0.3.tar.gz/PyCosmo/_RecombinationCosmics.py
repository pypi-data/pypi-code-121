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

__author__ = "AR & AA"

import numpy as np
from ._Cosmics import cosmics


class RecombinationCosmics:
    """
    Compute recombination and thermodynamic variables as a function of redshift. This is
    for debugging purposes and is done by reading an output file from COSMICS.
    """

    def __init__(self, params, cosmo):

        # initialise
        self._params = params

        # call RECFAST++ to compute reionisation history tables
        print("Reading COSMICS recombination file")

        assert (
            self._params.recomb_filename is None
        ), "for cosmics setting the file name is not supported"

        tab_cosmics = cosmics(self._params.recomb_dir)

        self.eta = tab_cosmics.eta_th  # conformal time [h^-1 Mpc]
        # TODO: use internal pycosmo routines to convert eta into a rather than COSMICS
        # tables
        aa = np.logspace(np.log10(1e-4), np.log10(1.0), 500)
        etaa = cosmo.background.eta(aa)
        self.a = np.interp(self.eta, etaa, aa)  # scale factor [1]
        # TODO: check sign for taudot
        self.taudot = (
            -tab_cosmics.opaca2_th / tab_cosmics.h / self.a**2
        )  # taudot=dtau/deta [h Mpc^-1]
        self.cs2 = tab_cosmics.cs2_th  # baryon sound speed squared [1]
        self.tm = tab_cosmics.tempb_th  # Baryon (matter) temperature [K]

    def taudot_a(self, a):
        """
        Returns tau_dot=d(tau)/d(eta) where tau is the optical depth and eta is the
        conformal time as a function of the scale factor a
        :param a: scale factor [1]
        :return : tau_dot: conformal time derivative of the optical depth [h Mpc^-1]
        """
        # TODO: check for out of bound interpolations
        # return -np.interp(a, self.a[::-1], self.taudot[::-1] * self.a[::-1]**2) / a**2
        # # tau_dot [h Mpc^-1]
        return (
            np.interp(a, self.a, self.taudot * self.a**2) / a**2
        )  # tau_dot [h Mpc^-1]

    def cs_a(self, a):
        """
        Returns the baryon sound speed as a function of the scale factor a
        :param a: scale factor [1]
        :return : cs: baryon sound speed [1]
        """

        # TODO: check for out of bound interpolations
        return np.sqrt(np.interp(a, self.a, self.cs2 * self.a) / a)  # sound speed [1]
