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

import os

import numpy as np


class RecombinationClass:
    """
    Compute recombination and thermodynamic variables as a function of redshift. This is
    for debugging purposes and is done by reading an output file from CLASS.
    """

    def __init__(self, params):

        # initialise
        self._params = params

        # call RECFAST++ to compute reionisation history tables
        print("Reading CLASS recombination file")

        # TODO: to be safer use h values from class rather than from PyCosmo
        # TODO: change path to avoid it being relative to recomb class
        tab_class = np.loadtxt(
            os.path.join(
                self._params.recomb_dir,
                self._params.recomb_filename,
            )
        )
        self.z = tab_class[:, 0]  # z [1]
        self.a = 1.0 / (1.0 + self.z)  # a [1]
        self.eta = tab_class[:, 1] * self._params.h  # eta [h^-1 Mpc]
        self.taudot = tab_class[:, 3] / self._params.h  # -taudot [h Mpc^-1]
        # baryon sound speed squared [1] Warning! This could be anything between 7 and
        # 9!!
        self.cs2 = tab_class[:, -2]

    def taudot_a(self, a):
        """
        Returns tau_dot=d(tau)/d(eta) where tau is the optical depth and eta is the
        conformal time as a function of the scale factor a

        :param a: scale factor [1]

        :return : tau_dot: conformal time derivative of the optical depth [h Mpc^-1]
        """

        # assert np.all(a >= np.min(self.a)) and np.all(a <= np.max(self.a))
        return (
            -np.interp(a, self.a[::-1], self.taudot[::-1] * self.a[::-1] ** 2) / a**2
        )  # tau_dot [h Mpc^-1]

    def cs_a(self, a):
        """
        Returns the baryon sound speed as a function of the scale factor a

        :param a: scale factor [1]

        :return : cs: baryon sound speed [1]
        """

        # assert np.all(a >= np.min(self.a)) and np.all(a <= np.max(self.a))
        return np.sqrt(
            np.interp(a, self.a[::-1], self.cs2[::-1] * self.a[::-1]) / a
        )  # sound speed [1]
