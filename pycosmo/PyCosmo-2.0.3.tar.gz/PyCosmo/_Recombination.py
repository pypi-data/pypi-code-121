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

from functools import lru_cache
import warnings

import numpy as np

from ._scipy_utils import interp1d

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from recfast4py import recfast


Xe_frac = lru_cache()(recfast.Xe_frac)


class Recombination:
    """
    Compute recombination and thermodynamic variables as a function of redshift. This is
    based on a call to RECFAST++.
    """

    # TODO: add reference for RECFAST++ and also make it compatible with other
    # recombination codes

    def __init__(self, params):

        # initialise
        self.params = params

        # call RECFAST++ to compute reionisation history tables
        # TODO: change name from RECFAST to RECFAST++ in code
        # TODO: check F and fDM parameters

        assert self.params.Tcmb > 0.01

        self.z, self.xe_h, self.xe_he, self.xe, self.tm = Xe_frac(
            self.params.Yp,
            self.params.Tcmb,
            self.params.omega_m,
            self.params.omega_b,
            self.params.omega_l,
            self.params.omega_k,
            self.params.h,
            self.params.N_massless_nu,
            self.params.F,  # F and fDM need testing
            self.params.fDM,
        )
        self.a = 1.0 / (1.0 + np.array(self.z))  # scale factor [1]

        # build functions of arbitrary a by interpolating and extrapolating for early
        # times
        # TODO: document these functions
        # TODO: check that this extrapolation ot max value at high z and that xe=1.2>1
        # at early times is OK
        self.xe_a = interp1d(
            self.a, self.xe, bounds_error=False, fill_value=np.max(self.xe)
        )  # total free electron fraction Xe [1]
        self.xe_h_a = interp1d(
            self.a, self.xe_h, bounds_error=False, fill_value=np.max(self.xe_h)
        )  # H free electron fraction XeH [1]
        self.xe_he_a = interp1d(
            self.a, self.xe_he, bounds_error=False, fill_value=np.max(self.xe_he)
        )  # He free electron fraction XeHe [1]

        # Compute logarithmic derivative of the baryon temperature
        lna = np.log(self.a)
        n_a = self.a.size
        dlntmdlna = np.zeros(
            n_a
        )  # logarithmic derivative dTm_dln(a) of the baryon temperature [1]
        a_dlntmdlna = np.zeros(n_a)
        for i in range(0, n_a - 1):
            a_dlntmdlna[i] = np.exp(0.5 * (lna[i] + lna[i + 1]))
            dlntmdlna[i] = (np.log(self.tm[i + 1]) - np.log(self.tm[i])) / (
                lna[i + 1] - lna[i]
            )
        a_dlntmdlna[n_a - 1] = 1.0  # fill in a=1 value - Warning: a bit dangerous
        dlntmdlna[n_a - 1] = -2.0
        dlntmdlna_max = np.max(dlntmdlna)
        self.dlntmdlna_a = interp1d(
            a_dlntmdlna, dlntmdlna, bounds_error=False, fill_value=dlntmdlna_max
        )  # d(Tm)/d(ln a) [1]

    def taudot_a(self, a):
        """
        Return tau_dot the derivative of the optical depth with respect to conformal
        time
        :param a:
        ;return: taudot: tou_dot=d(tau)/d(eta) [h Mpc^-1]
        """

        taudot_norm = (
            self.params.sigmat
            * (self.params.rho_crit * self.params.msun / self.params.mpc**3)
            / (self.params.mp * 1e6 * self.params.evc2)
        )  # sigma_thomson*rho_crit/m_p= 7.471e-28 h^2 m^-1
        return (
            -taudot_norm
            * self.params.mpc
            / a**2
            * self.xe_a(a)
            * self.params.omega_b
            * self.params.h
            * (1.0 - self.params.Yp)
        )  # [h Mpc^-1] (see Dodelson eq. 3.44, p73) + 1-Y factor from COSMICS)

    def _tm_a(self, a):
        """
        Return the Baryon (matter) temperature as a function of the scale factor a,
        by interpolating (or extrapolating for early times) the recombination tables.
        :param a: scale factor [1]
        :return: Baryon (matter) temperature Tm [K]
        """

        aa = np.array(a)
        n_a = aa.size
        tm = np.zeros(n_a)

        flags = aa < np.min(self.a)
        tm[flags] = self.params.Tcmb / aa[flags]
        tm[~flags] = np.exp(
            np.interp(np.log(aa[~flags]), np.log(self.a), np.log(self.tm))
        )

        return tm

    def _mu_a(self, a):
        """
        Computes the dimensonless mean molecular weight. It can be multiplied by the
        hydrogen atom mass to express it in mass units.
        :param a: a - scale factor [1]
        :return: mu: dimensionless mean molecular weight [1] (multiply bu the hydrogen
        atom mass to express in units of mass)
        """

        return 1.0 / (
            (1.0 + self.xe_h_a(a)) * (1.0 - self.params.Yp)
            + 0.25 * (1.0 + 2.0 * self.xe_he_a(a)) * self.params.Yp
        )

    def cs_a(self, a):
        """
        Returns the baryon sound speed
        :param a: scale factor [1]
        :return : cs: baryon sound speed [1]

        """

        tma = self._tm_a(a)
        mua = self._mu_a(a)
        dln = self.dlntmdlna_a(a)
        return np.sqrt(
            self.params.kb * tma / mua / (self.params.mp * 1e6) * (1.0 - dln / 3.0)
        )
