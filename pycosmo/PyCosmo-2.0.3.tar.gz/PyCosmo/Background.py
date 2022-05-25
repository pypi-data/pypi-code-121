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
from scipy import integrate


def _call(wrapper, function, a=None):
    if a is None:
        return getattr(wrapper, function)()
    elif isinstance(a, (float, int)):
        return getattr(wrapper, function)(a)
    elif isinstance(a, list):
        a = np.array(a)
    assert isinstance(a, np.ndarray)
    a = a.astype(float)
    return getattr(wrapper, function + "_ufunc")(a)


class Background(object):
    """
    The background calculations are based on a
    Friedmann-Robertson-Walker model for which the evolution is governed by
    the Friedmann equation.
    """

    # The first part contains the functions that deal with the elements
    # of the Friedmann equation.  In particular the focus in the Hubble
    # function. In the PyCosmo notes, this is section 1.2

    def __init__(self, cosmo, params, rec, wrapper):
        self._cosmo = cosmo
        self._params = params
        self._rec = rec
        self._wrapper = wrapper

    def H(self, a):
        """
        Calculates the Hubble parameter for a given scale factor
        by calling the expression from CosmologyCore_model.py.

        :param a: scale factor [1]
        :return: Hubble parameter :math:`H(a) [km/s/Mpc]`.

        Example:

        .. code-block:: python

            cosmo.background.H(a)
        """
        self._cosmo.reset_wrapper_globals()
        return _call(self._wrapper, "H", a)

    _hubble = H

    def _H2_H02_a(self, a=1.0):
        return (
            self._H2_H02_Omegar_a(a=a)
            + self._H2_H02_Omegam_a(a=a)
            + self._H2_H02_Omegak_a(a=a)
            + self._H2_H02_Omegal_a(a=a)
        )

    def _H2_H02_Omegar_a(self, a=1.0):
        return self._params.omega_r / a**4

    def _H2_H02_Omegam_a(self, a=1.0):
        self._cosmo.reset_wrapper_globals()
        return (
            self._params.omega_m / a**3
            + _call(self._wrapper, "omega_nu_m", a) / a**4
        )

    def _H2_H02_Omegak_a(self, a=1.0):
        return self._params.omega_k / a**2

    def _H2_H02_Omegal_a(self, a=1.0):
        self._cosmo.reset_wrapper_globals()
        return _call(self._wrapper, "omega_l_a", a)

    def _H2_H02_Omega_nu_m_a(self, a=1.0):
        self._cosmo.reset_wrapper_globals()
        return _call(self._wrapper, "omega_nu_m", a) / a**4

    def _w_a(self, a=1.0):
        return self._params.w0 + (1.0 - a) * self._params.wa

    #########################################################
    #  A series of functions for calculating                #
    #  cosmological distances:                              #
    #########################################################

    #
    # TODO: have a closer look at this method, can we compile this?
    # math formula should be in notebook

    def dist_rad_a(self, a=1.0):
        r"""
        Calculates the radial comoving distance, also known as the comoving radius.

        :param a: scale factor [1]
        :return: Radial comoving distance, :math:`\chi(a)`, in :math:`[Mpc]`.

        Example:

        .. code-block:: python

            cosmo.background.dist_rad_a(a)

        """

        return self._chi(a) * self._params.c

    def _chi(self, a):
        r"""
        Calculates the comoving horizon, by calling the CosmologyCore_model.py

        :param a: scale factor [1]
        :return: Radial comoving horizon, :math:`\chi(a)`, in :math:`[Mpc s/km]`.
        """
        self._cosmo.reset_wrapper_globals()
        return _call(self._wrapper, "chi", a)

    def dist_trans_a(self, a=1.0):
        r"""
        Calculates the transverse comoving distance, also known as comoving
        angular-diameter distance.

        :param a: scale factor [1]
        :return: Transverse comoving distance, :math:`r(\chi)`, in :math:`[Mpc]`.

        Example:

        .. code-block:: python

            cosmo.background.dist_trans_a(a)
        """

        Dc = self.dist_rad_a(a)
        if self._params.omega_k == 0.0:
            Dm = Dc
        elif self._params.omega_k > 0.0:
            Dm = (
                self._params.rh
                * np.sinh(self._params.sqrtk * Dc / self._params.rh)
                / self._params.sqrtk
            )
        elif self._params.omega_k < 0.0:
            Dm = (
                self._params.rh
                * np.sin(self._params.sqrtk * Dc / self._params.rh)
                / self._params.sqrtk
            )
        return Dm

    def dist_ang_a(self, a=1.0):
        """
        Calculates the angular-diameter distance to a given scale factor.

        :param a: scale factor [1]
        :return: Angular diameter distance, :math:`D_A(a)`, in :math:`[Mpc]`.

        Example:

        .. code-block:: python

            cosmo.background.dist_ang_a(a)
        """

        return self.dist_trans_a(a) * a

    def dist_lum_a(self, a=1.0):
        """
        Calculates the luminosity distance to a given scale factor.

        :param a: scale factor [1]
        :return: Luminosity distance, :math:`D_L(a)`, in :math:`[Mpc]`.

        Example:

        .. code-block:: python

            cosmo.background.dist_lum_a(a)
        """

        return self.dist_trans_a(a) / a

    def eta(self, a):
        r"""
        Calculates conformal time :math:`\eta` to a given scale factor.

        :param a: scale factor [1]
        :return: :math:`\eta` conformal time [:math:`\mathrm{Mpc}/h`]
        """
        a = np.atleast_1d(a)
        self._cosmo.reset_wrapper_globals()
        return _call(self._wrapper, "eta", a)  # Mpc/h

    #########################################################
    # A series of functions to compute thermodynamical      #
    # variables including recombination                     #
    #########################################################

    def taudot(self, a=1.0):
        r"""
        Calculates :math:`\dot{\tau} = \frac{d\tau}{d\eta}`,
        where :math:`\tau` is the optical depth and :math:`\eta` is the conformal time.

        :param a: scale factor [1]
        :return: :math:`\dot{\tau} = \frac{d\tau}{d\eta}` in units of
                [:math:`h \mathrm{Mpc}^{-1}`]

        Example:

        .. code-block:: python

            cosmo.background.taudot(a)
        """

        a = np.atleast_1d(a)
        return self._rec.taudot_a(a)  # h/Mpc

    def cs(self, a):
        """
        Returns the photon-baryon fluid sound speed [1]
        from the Recombination module

        :param a: scale factor [1]
        :return: cs: photon-baryon sound speed [1]

        Example:

        .. code-block:: python

            cosmo.background.cs(a)
        """
        a = np.atleast_1d(a)
        return self._rec.cs_a(a)

    # Flagged: More comments needed, might need to be speed up at some point.
    def tau(self, a=1.0):
        """
        Calculates the optical depth of the photon-baryon fluid,
        by integrating taudot from the Recombination module.

        :param a: scale factor [1]
        :return: tau: optical depth [1]

        Example:

        .. code-block:: python

            cosmo.background.tau(a)
        """
        a = np.atleast_1d(a)
        return np.array(
            [integrate.quadrature(self._tau_intgd, np.log(aa), 0.0)[0] for aa in a]
        )

    def _tau_intgd(self, lna):
        a = np.exp(lna)
        return -self.taudot(a=a) / (a * self.H(a=a) / self._params.H0 / self._params.rh)

    def tau_b(self, a=1.0):
        """
        Calculates the optical depth of the baryon fluid,
        by integrating taudot from the Recombination module,
        weighted with R, the baryon-photon fraction.

        :param a: scale factor [1]
        :return: tau: optical depth [1]

        Example:

        .. code-block:: python

            cosmo.background.tau(a)
        """
        a = np.atleast_1d(a)
        return np.array(
            [
                integrate.quadrature(
                    self._tau_b_intgd, np.log(aa), 0.0, maxiter=100, rtol=5e-5
                )[0]
                for aa in a
            ]
        )

    def _tau_b_intgd(self, lna):
        a = np.exp(lna)
        result = -self.taudot(a=a) / (
            a**2
            * self.H(a=a)
            / self._params.H0
            / self._params.rh
            * 3
            * self._params.omega_b
            / (4 * self._params.omega_gamma)
        )
        return result

    def g_a(self, a=1.0):
        """
        Calculates the visibility function for a given scale factor.

        :param a: scale factor [1]
        :return: visibility function [1/Mpc]

        Example:

        .. code-block:: python

            cosmo.background.g_a(a)
        """
        a = np.atleast_1d(a)
        return -self.taudot(a) * np.exp(-self.tau(a)) * self._params.h

    def r_s(self):
        r"""
        Calculates the sound horizon at drag epoch.

        :return: sound horizon [:math:`\mathrm{Mpc} / h`]
        """
        a_log = np.logspace(np.log10(2e-4), np.log10(2e-3), 200)
        a_drag = np.where(self.tau_b(a_log) >= 1.0)[0]

        if not len(a_drag):
            return np.inf
        a_drag = a_drag[-1]

        return integrate.quadrature(self._r_s_intg, np.log(a_drag), 0.0, rtol=1e-5)[
            0
        ]  # Mpc/h

    def _r_s_intg(self, lna):
        a = np.exp(lna)
        return -1 / (
            a
            * self.H(a=a)
            / self._params.H0
            / self._params.rh
            * np.sqrt(3 * self._params.omega_b / (4 * self._params.omega_gamma) * a)
        )

    def _r_bph_a(self, a=1.0):  # baryon to photon ratio r_bph(a) [1]
        return 3.0 / 4.0 * self._params.omega_b / self._params.omega_gamma * a

    def _cs_approx(self, a):  # photon-baryon fluid sound speed [1]
        # this is a simple expression which is probably a simple approximation - needs
        # refining
        return np.sqrt(1.0 / (3.0 * (1.0 + self._r_bph_a(a))))

    def _dlnh_dlna(self, a=1.0):
        a = np.atleast_1d(a)
        temp = (
            -0.5
            / self._H2_H02_a(a)
            * (
                3.0 * self._H2_H02_Omegam_a(a=a)
                + 3.0 * (1.0 + self._w_a(a)) * self._H2_H02_Omegal_a(a=a)
                + 2.0 * self._H2_H02_Omegak_a(a=a)
            )
        )

        return temp

    #########################################################
    # The next section lists a set of functions for         #
    # calculating the density parameters as a function of   #
    # a. This is also consistent with the notes in          #
    # section 1.2 of the PyCosmo notes.                     #
    #########################################################

    def _omega_m_a(self, a=1.0):
        """
        Calculates the matter density for a given scale factor
        (includes massive neutrinos as matter)
        input: a - scale factor [1]
        output: [1]
        """
        return self._H2_H02_Omegam_a(a=a) / self._H2_H02_a(a=a)

    def _omega_r_a(self, a=1.0):
        """
        Calculates the radiation density for a given scale factor
        includes photons and massless neutrinos
        input: a - scale factor [1]
        output: [1]
        """
        return self._H2_H02_Omegar_a(a=a) / self._H2_H02_a(a=a)

    def _omega_l_a(self, a=1.0):
        """
        Calculates the dark energy density for a given scale factor
        input: a - scale factor [1]
        output: [1]
        """
        return self._H2_H02_Omegal_a(a=a) / self._H2_H02_a(a=a)

    def _omega_nu_m_a(self, a=1.0):
        """
        Calculates the massive neutrinos density for a given scale factor
        input: a - scale factor [1]
        output: [1]
        """
        return self._H2_H02_Omega_nu_m_a(a=a) / self._H2_H02_a(a=a)

    def _omega_a(self, a=1.0):
        """
        Calculates the total density for a given scale factor
        input: a - scale factor [1]
        output: [1]
        """
        return (
            self._omega_m_a(a=a)
            + self._omega_r_a(a=a)
            + self._omega_l_a(a=a)
            + self._omega_nu_m_a(a=a)
        )

    def _omega_k_a(self, a=1.0):
        """
        Calculates the curvature for a given scale factor
        input: a - scale factor [1]
        output: [1]
        """
        return 1.0 - self._omega_a(a=a)
