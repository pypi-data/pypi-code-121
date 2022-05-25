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
from scipy import integrate, special

from .LinearPerturbationBase import LinearPerturbationBase


class LinearPerturbationApprox(LinearPerturbationBase):

    r"""
    Class created to manage fitting functions for the computation of the linear matter
    power spectrum :math:`P_{lin}(k)`.  The fitting functions provide transfer
    functions that are then used to compute the power spectrum.

    The different fitting functions can be selected using the *set function*:

        .. code-block:: python

            cosmo.set(pk_type = option)

        where *option* can be one the following keywords:

        - ``EH`` for `Eisenstein & Hu, 1998, ApJ, 511, 5 (default)
            <https://arxiv.org/abs/astro-ph/9710252>`_
        - ``BBKS`` for BBKS as summarized by `Peacock, 1997, MNRAS, 284, 885
            <https://arxiv.org/abs/astro-ph/9608151>`_

        **For developers:** in order to compare the codes :math:`\textsf{PyCosmo}` and
        :math:`\texttt{CCL}` in terms of linear matter power spectrum computed with
        the *BBKS* fitting function, the user should choose a routine which is
        optimized for this purpose. This further option can be selected as:

        .. code-block:: python

            cosmo.set(pk_type = 'BBKS_CCL')

        where ``BBKS_CCL`` follows the implementation in the
        `CCL code <https://arxiv.org/abs/1812.05995>`_ .

    """

    def __init__(self, cosmo):
        self._cosmo = cosmo
        self._params = cosmo.params
        self._background = cosmo.background

        self._enrich_params()

    def max_redshift(self, k):
        """computes max redshift for which this model is applicable.

        :param k: wavenumber k, introduced in the abstract base class since this
                  might be needed for some models.
                  [:math:`h Mpc^{-1}`]
        :returns: redshift
        """
        avec = np.linspace(1e-4, 1, 10000)
        ai = avec[np.argmax(self._background._omega_m_a(avec))]
        return 1 / ai - 1

    def _D1(self, a=1.0, norm=0):
        """
        Computes the linear growth factor :math:`D(a)` by integrating the growth
        differential equation.

        :param a: scale factor [1]
        :param norm: normalisation scheme: 0: D(a=1)=1 (default), 1:
                     D(a)=a in matter era,

        .. code-block:: python

            cosmo.lin_pert.growth_a(a)
        """
        # assert k is None, 'this model {} does not consider k'.format(self)
        a = np.atleast_1d(a)

        ai = 1.0 / (self.max_redshift(None) + 1)
        a_start = min(
            np.concatenate((a, np.array([ai])))
        )  # initial condition for integration
        if a_start < ai:
            raise ValueError(f"initial a_start={a_start} too high (at max {ai})")

        a = np.atleast_1d(a)
        a_out = np.concatenate((np.array([a_start]), a, np.array([1.0])))

        perm = np.argsort(a_out)  # keeping track of index that would sort the array a
        inverse_perm = np.argsort(perm)  # useful indec for going back to original
        a_out = a_out[perm]
        y_start = np.array([1.0, 0.0])  # initial conditions: y1=G=1, y2=dG/dlna=0.
        x_out = np.log(a_out)

        u = integrate.odeint(self._growth_derivs, y_start, x_out)

        u0 = u[:, 0][inverse_perm]
        if norm == 0:
            D = u0[1:-1] * a / u0[-1]  # normalise to D=1 at a=1
        elif norm == 1:
            D = u0[1:-1] * a  # normalise to D=a in matter dominated era
        else:
            raise ValueError("invalid value for norm, must be 0 or  1")
        return D

    def growth_a(self, a, k=None, norm=0, diag_only=True):
        """
        Returns the linear growth factor by calling a function that
        integrates the growth differential equation.
        It returns a vector of len(a) if k is None or a number, or if diag_only is set
        to True.  Otherwise it returns a matrix with dimension (len(k), len(a)).

        :param a: scale factor [1]
        :param k: wavenumber k, necessary for massive neutrino models
                  [:math:`h Mpc^{-1}`]
        :param norm: normalisation scheme: norm = 0: D(a=1)=1 (default),
                     norm = 1: D(a)=a in matter era
        :param diag_only: if set to False, the growth factor is repeated and
                    reshaped to match the shape of k
        :return: growth factor [1]
        """

        if (
            self._params.massive_nu_total_mass == 0.0
            or self._params.N_massive_nu == 0.0
        ):
            if k is None or np.isscalar(k) or diag_only:
                return self._D1(a, norm)
            k = np.atleast_1d(k)
            return np.repeat(self._D1(a, norm).reshape(1, -1), len(k), axis=0)

        if k is None:
            raise ValueError(
                "You must specify k since growth factor in EH with heavy neutrinos is"
                " k dependent!"
            )

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)

        if diag_only:
            assert a.shape == k.shape, "in diag_only mode a and k must have same length"

        growth_nu = self._D1(a, norm=1) * (1.0 + self._params._z_equality)
        term_1 = self._D1(a) * growth_nu ** (-self._params._p_cb)
        if diag_only:
            return term_1 * self._D_cb_diag(growth_nu, k)
        return term_1 * self._D_cb(growth_nu, k)

    def _growth_derivs(self, y, x):
        """Compute derivatives for the ODE for calcuting the growth factor.
        !!!NEED TO INCLUDE REFERENCE!!!
        """
        a_temp = np.exp(
            np.array(x)
        )  # ; x=ln(a) #; compute derivatives of y1=G and y2=dG/dlna
        f1 = y[1]  # f1=dy1/dx=y2=dG/dlna

        _dlnh_dlna = self._background._dlnh_dlna(a=a_temp)

        f2 = (
            -(4.0 + _dlnh_dlna) * y[1]
            - (3.0 + _dlnh_dlna - 1.5 * self._background._omega_m_a(a=a_temp)) * y[0]
        )
        return [f1, f2]

    def _growth_derivs_nu(self, y, x):
        """Compute derivatives for the ODE for calcuting the growth factor including
        massive neutrinos.
        !!!NEED TO INCLUDE REFERENCE!!!
        """
        a_temp = np.exp(
            np.array(x)
        )  # ; x=ln(a) #; compute derivatives of y1=G and y2=dG/dlna
        f1 = y[1]  # f1=dy1/dx=y2=dG/dlna

        _dlnh_dlna = self._background._dlnh_dlna_massive_nu(a=a_temp)

        f2 = (
            -(4.0 + _dlnh_dlna) * y[1]
            - (3.0 + _dlnh_dlna - 1.5 * self._background._omega_m_a(a=a_temp)) * y[0]
        )
        return [f1, f2]

    def _growth_hyper_a(self, a=1.0):  # , Om=0.25,z=0):
        """
        LCDM growth function D(z) using hypergeometric function. Only
        valid for LCDM.
        This comes from Aseem Paranjape and is used for testing.
        ; param: a: scale factor
        ; return: D(a): growth factor normalised to 1 at a=1.
        """
        a = np.atleast_1d(a)
        a_temp = np.append(a, [1.0])
        acube = a_temp**3
        hbyh0 = np.sqrt(self._background._H2_H02_a(a=a_temp))
        g = (
            hbyh0
            / np.sqrt(self._params.omega_m)
            * np.power(a_temp, 2.5)
            * special.hyp2f1(
                5.0 / 6, 1.5, 11.0 / 6, -acube * (1.0 / self._params.omega_m - 1)
            )
        )
        g /= g[-1]  # normalised to 1 at a=1.0
        return g[:-1]

    def transfer_k(self, k):
        r"""
        Computes the linear matter transfer function using a choice of the currently
        available fitting functions.

        :param k: wavenumber :math:`[Mpc^{-1}]`
        :return: Matter transfer function :math:`T(k)` in :math:`Mpc^{3/2}`.

        """
        if self._params.pk_type == "EH":
            if (
                self._params.massive_nu_total_mass == 0.0
                or self._params.N_massive_nu == 0.0
            ):
                tk = self._transfer_EH(k)
            else:
                tk = self._T_master(k)
        elif self._params.pk_type in ("BBKS", "BBKS_CCL"):
            tk = self._transfer_BBKS(k)
        else:
            print(
                "transfer_k: error - only EH and BBKS fitting functions are supported"
            )

        return tk

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        """
        Computes the linear total matter power spectrum, :math:`P_{lin}(k)`, using a
        choice of fitting functions.

        :param a: scale factor [1]
        :param k: wavenumber :math:`[Mpc]^{-1}`
        :param diag_only: if set to True: compute powerspectrum for pairs
                           :math:`a_i, k_i`, else consider all combinations
                           :math:`a_i, k_j`
        :return: Linear matter power spectrum, :math:`P_{lin}(k)`, in :math:`[Mpc]^3`.

        Example:

        .. code-block:: python

            cosmo.set(pk_type = option)
            cosmo.lin_pert.powerspec_a_k(a,k)

        where ``option`` can be set to one of the fitting functions (``EH`` or
        ``BBKS``).
        """

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        if diag_only:
            assert len(a) == len(k)
        T_k = self.transfer_k(k=k)
        growth = self.growth_a(a, k, diag_only=diag_only)
        # using equation in section 2.4 of notes
        norm = (
            2.0
            * np.pi**2
            * self._params.deltah_norm**2
            * (self._params.c / self._params.H0) ** (3.0 + self._params.n)
        )

        if diag_only:
            pk = norm * growth**2 * k**self._params.n * T_k**2
        else:
            pk = norm * growth**2 * (k**self._params.n * T_k**2).reshape(-1, 1)
        return pk

    def _transfer_BBKS(self, k):
        """
        BBKS transfer function as summarized by Peacock (1997, MNRAS, 284, 885)

        :param  k: wavenumber [Mpc^-1]
        :return: T(k): BBKS matter transfer function [1]
        """
        k = np.atleast_1d(k)
        q_pd = k / self._params.h / self._params.gamma

        if self._params.pk_type == "BBKS_CCL":
            tfac = self._params.Tcmb / 2.7
            q_pd = q_pd * tfac**2

        tk = (
            np.log(1.0 + 2.34 * q_pd)
            / (2.34 * q_pd)
            * (
                1.0
                + 3.89 * q_pd
                + (16.1 * q_pd) ** 2
                + (5.46 * q_pd) ** 3
                + (6.71 * q_pd) ** 4
            )
            ** (-0.25)
        )

        return tk

    def _transfer_EH(self, k):
        """Return the CDM + baryon transfer function as defined in
        Eisenstein & Hu, 1998, ApJ, 511, 5, Equation (16) Input: wave
        vector k in Mpc^-1"""

        T = self._params.omega_b / self._params.omega_m * self._T_b(
            k
        ) + self._params.omega_dm / self._params.omega_m * self._T_c(k)

        return T

    def _jn_spher(self, n, x):
        """Returns the spherical Bessel function of order n.
        This is used to compute the oscillatory feature of the baryonic
        transfer function as in Eisenstein & Hu, 1998, ApJ, 511, 5"""

        jn_spher = np.sqrt(np.pi / (2.0 * x)) * special.jn(n + 0.5, x)

        return jn_spher

    def _G(self, y):
        """Returns the function G as defined in Eisenstein & Hu, 1998,
        ApJ, 511, 5, Equation (15)
        G(y) = y(-6. sqrt(1 + y) + (2 + 3 y) ln((sqrt(1 + y) + 1)/(sqrt(1 + y) - 1)))
        and needed to calculate alpha_b"""

        G = y * (
            -6.0 * np.sqrt(1.0 + y)
            + (2.0 + 3.0 * y)
            * np.log((np.sqrt(1.0 + y) + 1.0) / (np.sqrt(1.0 + y) - 1.0))
        )

        return G

    def _photon2baryon_dens(self, z):
        """Returns the ratio of the baryon to photon momentum density R
        as defined in Eisenstein & Hu, 1998, ApJ, 511, 5, Equation (5)
        for redshift z
        R = 31.5 omega_b h^2 sigma_27^-4 (z/10^3)^-1"""

        R = (
            31.5
            * self._params.omega_b
            * self._params.h**2
            * self._params._sigma_27 ** (-4)
            * (z / 10**3) ** (-1.0)
        )

        return R

    def _T_0(self, k, alpha_c, beta_c):
        """Returns the transfer function T_0 as defined in Eisenstein &
        Hu, 1998, ApJ, 511, 5, Equation (19)

        T_0 = ln(e+1.8 beta_c q)/(ln(e+1.8 beta_c q) + C q^2)

        where
        q = (k [Mpc^-1])/(13.41 k_eq)
        C = 14.2/alpha_c + 386/(1+69.9 q^1.08)
        alpha_c = a_1^(-omega_b/omega_0) a_2^(-(omega_b/omega_0)^3)
        a_1 = (46.9 omega_0 h^2)^0.670 (1+(32.1 omega_0 h^2)^-0.532)
        a_2 = (12.0 omega_0 h^2)^0.424 (1+(45.0 omega_0 h^2)^-0.582)
        beta_c^-1 = 1 + b_1 ((omega_c/omega_0)^b_2 - 1)
        b_1 = 0.944 (1 + (458 omega_0 h^2)^-0.708)^-1
        b_2 = (0.395 omega_0 h^2)^-0.0266"""

        # Define the needed variables as in Eqs. (10), (20)
        q = k / (13.41 * self._params._k_eq)
        C = 14.2 / alpha_c + 386.0 / (1.0 + 69.9 * q**1.08)

        T_0 = np.log(np.e + 1.8 * beta_c * q) / (
            np.log(np.e + 1.8 * beta_c * q) + C * q**2
        )

        return T_0

    def _T_b(self, k):
        """Returns the baryonic part of the transfer function as defined
        in Eisenstein & Hu, 1998, ApJ, 511, 5, Equation (21)

        T_b = (T_0(k,1,1)/(1 + (k s/5.2)^2)
                + alpha_b/(1 + (beta_c/(k s))^3)*e^-(k/k_Silk)^1.4
               ) *j_0(k s_tilde)
        """

        # Define the needed variable as in Eq. (22)
        s_tilde = self._params._sound_horiz / (
            1.0 + (self._params._beta_node / (k * self._params._sound_horiz)) ** 3
        ) ** (1.0 / 3.0)

        T_b = (
            self._T_0(k, 1.0, 1.0) / (1.0 + (k * self._params._sound_horiz / 5.2) ** 2)
            + self._params._alpha_b
            / (1.0 + (self._params._beta_b / (k * self._params._sound_horiz)) ** 3.0)
            * np.exp(-((k / self._params._k_Silk) ** 1.4))
        ) * self._jn_spher(0, k * s_tilde)

        return T_b

    def _T_c(self, k):
        """Returns the CDM part of the transfer function as defined in
        Eisenstein & Hu, 1998, ApJ, 511, 5, Equation (17)
        T_c = f T_0(k,1,beta_c) + (1 - f) T_0(k,alpha_c,beta_c)
        """

        f = 1.0 / (1.0 + (k * self._params._sound_horiz / 5.4) ** 4)  # Eq. (18)

        T_c = f * self._T_0(k, 1.0, self._params._beta_c) + (1.0 - f) * self._T_0(
            k, self._params._alpha_c, self._params._beta_c
        )

        return T_c

    def _gamma_eff(self, k):
        """
        :param k: wave vector k in Mpc^-1
        :return: scale-dependent rescaling of the zero-baryon shape parameter gamma
        defined in Eisenstein & Hu, 1999, ApJ, 511, 1, Equation (16)
        Gamma_eff =\
        Omega_0 * h^2 * (sqrt(alpha_nu) + (1 - sqrt(alpha_nu)) / (1 + (0.43 * k * s)^4))
        """

        gamma_eff = (
            (self._params.omega_m + self._params.omega_nu_m)
            * self._params.h**2
            * (
                np.sqrt(self._params._alpha_nu)
                + (1.0 - np.sqrt(self._params._alpha_nu))
                / (1.0 + (0.43 * k * self._params._sound_horiz_nu) ** 4.0)
            )
        )

        return gamma_eff

    def _q_eff(self, k):
        """
        :param k: wave vector k in Mpc^-1
        :return: scale-dependent equation (17) defined in Eisenstein & Hu, 1999, ApJ,
                  511, 1
                  q_eff = k * Sigma_2.7^2 / (Gamma_eff * Mpc^-1)
        """
        q_eff = k * self._params._sigma_27**2.0 / self._gamma_eff(k)

        return q_eff

    def _T_master(self, k):
        """
        :param k: wave vector k in Mpc^-1
        :return: scale-dependent but time-independent master function defined in
        Eisenstein & Hu, 1999, ApJ, 511, 1, Equation (24)
        T_master(k) = T_sup(k) * B(k)
        """
        return self._T_sup(k) * self._B(k)

    def _T_sup(self, k):
        """
        T_sup(k) = L / (L + C * q_eff^2)

        :param k: wave vector k in Mpc^-1
        :return: small-scale suppressed CDM + baryon + massive neutrinos transfer
                 function as defined in
                 Eisenstein & Hu, 1999, ApJ, 511, 1, Equation (18)
        """

        L = np.log(
            np.e
            + 1.84
            * self._params._beta_c_nu
            * np.sqrt(self._params._alpha_nu)
            * self._q_eff(k)
        )  # Eq. (19)
        C = 14.4 + 325.0 / (1.0 + 60.5 * self._q_eff(k) ** 1.08)  # Eq. (20)

        return L / (L + C * self._q_eff(k) ** 2)

    def _B(self, k):
        """
        :param k: wave vector k in Mpc^-1
        :return: returns the function B(k) defined by Eq. (22) in Eisenstein & Hu, 1999,
                 ApJ, 511, 1
        """

        assert self._params.N_massive_nu > 0, "need N_massive_nu > 0"
        assert self._params.massive_nu_total_mass > 0, "need massive_nu_total_mass > 0"

        q_nu = k / (
            3.42
            * np.sqrt(self._params._f_nu / self._params.N_massive_nu)
            * self._params._k_eq_nu
        )

        b_val = 1.0 + (
            1.24
            * (self._params._f_nu**0.64)
            * (self._params.N_massive_nu ** (0.3 + 0.6 * self._params._f_nu))
        ) / (q_nu**-1.6 + q_nu**0.8)

        return b_val

    def _y_fs(self, k):
        """
        :param k: wave vector k in Mpc^-1
        :return: free-streaming epoch as a function of scale defined by Eq. (14) in
        Eisenstein & Hu, 1999, ApJ, 511, 1
        """

        if self._params.massive_nu_total_mass == 0.0:
            return 0.0

        q = (
            k
            * self._params._sigma_27**2.0
            * ((self._params.omega_m + self._params.omega_nu_m) * self._params.h**2)
            ** -1.0
        )

        y_fs = (
            17.2
            * self._params._f_nu
            * (1.0 + 0.488 * self._params._f_nu ** -(7.0 / 6.0))
            * (self._params.N_massive_nu * q / self._params._f_nu) ** 2.0
        )

        return y_fs

    def _D_cb(self, growth_nu, k):
        """
        :param a: scale factor [1]
        :param k: wave vector k in Mpc^-1
        :return: DM + baryons growth rate in the presence of free-streaming defined by
                 Eq. (12) in Eisenstein & Hu, 1999, ApJ, 511, 1
        """
        return (1.0 + (np.outer(growth_nu, 1.0 / (1.0 + self._y_fs(k))).T) ** 0.7) ** (
            self._params._p_cb / 0.7
        )

    def _D_cb_diag(self, growth_nu, k):
        """
        :param a: scale factor [1]
        :param k: wave vector k in Mpc^-1
        :return: DM + baryons growth rate in the presence of free-streaming defined by
                 Eq. (12) in Eisenstein & Hu, 1999, ApJ, 511, 1
        """
        return (1.0 + (growth_nu / (1.0 + self._y_fs(k))) ** 0.7) ** (
            self._params._p_cb / 0.7
        )

    def _enrich_params(self):
        """Sets the constant parameters needed for the
        LinearPerturbationApprox class.  If pk_type = EH it sets the
        parameters needed for computing the transfer function as defined
        in Eisenstein & Hu, 1998, ApJ, 511, 5.

        If pk_type = BBKS it sets the parameters needed for computing
        the BBKS transfer function as summarized by Peacock (1997,
        MNRAS, 284, 885)
        """

        if self._params.pk_type == "EH":

            self._set_eh_params()

        if self._params.pk_type in ("BBKS", "BBKS_CCL"):
            """This calculates Gamma for the linear powerspectrum using the
            prescription Sugiyama (1995, APJS, 100, 281)"""
            gamma = (
                self._params.omega_m
                * self._params.h
                * np.exp(
                    -self._params.omega_b
                    * (1.0 + np.sqrt(2.0 * self._params.h) / self._params.omega_m)
                )
            )
            self._params.gamma = gamma

        # normalise linear power spectrum   #TODO: perhaps avoid writing in
        # params; perhaps needs more error checking
        if self._params.pk_norm_type == "deltah":
            self._params.deltah_norm = self._params.pk_norm
            self._params.sigma8 = self.sigma8()
        if self._params.pk_norm_type == "sigma8":
            self._params.sigma8 = self._params.pk_norm
            self._params.deltah_norm = 4.0e-5  # arbitrary temporary value
            sigma8_temp = self.sigma8()
            self._params.deltah_norm = (
                self._params.deltah_norm * self._params.sigma8 / sigma8_temp
            )
        if self._params.pk_norm_type == "A_s":
            raise NotImplementedError(
                "A_s normalization only available for the Boltzmann solver, \
                                        choose deltah or sigma8"
            )

        return None

    def _set_eh_params(self):

        if (
            self._params.N_massive_nu == 0.0
            or self._params.massive_nu_total_mass == 0.0
        ):
            omh2 = (
                self._params.omega_m + self._params.omega_nu_m
            ) * self._params.h**2

            self._params._k_Silk = (
                1.6
                * (self._params.omega_b * self._params.h**2) ** 0.52
                * (omh2) ** 0.73
                * (1.0 + (10.4 * omh2) ** -0.95)
            )  # Eq. (7), units: Mpc^-1

            # CDM transfer function, Equations (11), (12)

            a1 = (46.9 * omh2) ** 0.670 * (1.0 + (32.1 * omh2) ** -0.532)
            a2 = (12.0 * omh2) ** 0.424 * (1.0 + (45.0 * omh2) ** -0.582)
            self._params._alpha_c = a1 ** (
                -self._params.omega_b / self._params.omega_m
            ) * a2 ** (-((self._params.omega_b / self._params.omega_m) ** 3.0))

            b1 = 0.944 * (1.0 + (458.0 * omh2) ** -0.708) ** -1
            b2 = (0.395 * omh2) ** -0.0266
            self._params._beta_c = 1.0 / (
                1.0 + b1 * ((self._params.omega_dm / self._params.omega_m) ** b2 - 1.0)
            )

            # Baryon transfer function, Equations (14), (24), (23)

            # alpha_b = 2.07 k_eq s (1 + R_d)^-3/4 G((1 + z_eq)/(1 + z_d))
            # beta_b = 0.5 + omega_b/omega_m_0 + (3 - 2 omega_b/omega_m_0) sqrt((17.2
            # omega_m_0 h^2)^2 + 1)
            # b_node = 8.41 (omega_m_0 h^2)^0.435

            self._params._alpha_b = (
                2.07
                * self._params._k_eq
                * self._params._sound_horiz
                * (1.0 + self._params._R_drag) ** -0.75
                * self._G(
                    (1.0 + self._params._z_equality) / (1.0 + self._params._z_drag)
                )
            )
            self._params._beta_b = (
                0.5
                + self._params.omega_b / self._params.omega_m
                + (3 - 2 * self._params.omega_b / self._params.omega_m)
                * np.sqrt((17.2 * omh2) ** 2 + 1)
            )
            self._params._beta_node = 8.41 * omh2**0.435

        else:

            omh2_nu = (
                self._params.omega_m + self._params.omega_nu_m
            ) * self._params.h**2
            omb2_nu = self._params.omega_b * self._params.h**2

            # equations for massive neutrinos from Eisenstein & Hu, 1999, ApJ, 511, 1

            # Redshift at matter-radiation equality, Eq. (2) in Eisenstein & Hu, 1998,
            # ApJ, 496, 2 (modified to include Omega_nu_m in Omega_m)
            z_equality_nu = 2.5e4 * omh2_nu * self._params._sigma_27**-4
            b_1_nu = 0.313 * omh2_nu**-0.419 * (1.0 + 0.607 * omh2_nu**0.674)
            b_2_nu = 0.238 * omh2_nu**0.223
            z_drag_nu = (
                1291.0
                * (omh2_nu**0.251)
                / (1.0 + 0.659 * omh2_nu**0.828)
                * (
                    1.0
                    + b_1_nu * (self._params.omega_b * self._params.h**2) ** b_2_nu
                )
            )  # Redshift at drag epoch, Eq. (4)

            # Wave vector values, modified to include Omega_nu_m in Omega_m
            self._params._k_eq_nu = (
                7.46e-2 * omh2_nu * self._params._sigma_27**-2
            )  # Eq. (3), units: Mpc^-1

            # sound horizon given by Eq. (4) in Eisenstein & Hu, 1999, ApJ, 511, 1
            # (modified to include Omega_nu_m in Omega_m)
            self._params._sound_horiz_nu = (
                44.5
                * np.log(9.83 / omh2_nu)
                / np.sqrt(1.0 + 10.0 * omb2_nu ** (3.0 / 4.0))
            )

            # ratios of the density of the species DM, baryons and massive neutrinos to
            # the total matter density

            # 0..1
            f_c = self._params.omega_dm / (
                self._params.omega_dm + self._params.omega_b + self._params.omega_nu_m
            )

            # 0 without massuive nu:
            f_nu = self._params._f_nu = self._params.omega_nu_m / (
                self._params.omega_dm + self._params.omega_b + self._params.omega_nu_m
            )

            # 1 without massive nu:
            f_cb = (self._params.omega_dm + self._params.omega_b) / (
                self._params.omega_dm + self._params.omega_b + self._params.omega_nu_m
            )

            f_nub = (self._params.omega_nu_m + self._params.omega_b) / (
                self._params.omega_dm + self._params.omega_b + self._params.omega_nu_m
            )

            # Eq. (11) for DM only (p_c) and for DM + baryons (p_cb)
            p_c = (1.0 / 4.0) * (5.0 - np.sqrt(1.0 + 24.0 * f_c))

            # 0 without massive nu:
            p_cb = self._params._p_cb = (1.0 / 4.0) * (5.0 - np.sqrt(1.0 + 24.0 * f_cb))

            # Eq. (21)
            self._params._beta_c_nu = 1.0 / (1.0 - 0.949 * f_nub)

            # Eq. (3)
            y_d = (1.0 + z_equality_nu) / (1.0 + z_drag_nu)

            # Eq. (15)

            self._params._alpha_nu = (
                (f_c / f_cb)
                * (5.0 - 2 * (p_c + p_cb))
                / (5.0 - 4.0 * p_cb)
                * (
                    (1.0 - 0.553 * f_nub + 0.126 * f_nub**3.0)
                    / (1.0 - 0.193 * np.sqrt(f_nu) + 0.169 * f_nu)
                )
                * (1.0 + y_d) ** (p_cb - p_c)
                * (
                    1.0
                    + (p_c - p_cb)
                    / 2.0
                    * (1.0 + 1.0 / ((3.0 - 4.0 * p_c) * (7.0 - 4.0 * p_cb)))
                    * (1.0 + y_d) ** -1
                )
            )

    def print_params(self):
        """
        Print the parameters related to the chosen linear fitting function (*EH* or
        *BBKS*).

        Example:

        .. code-block:: python

            cosmo.lin_pert.print_params()

        """

        if self._params.pk_type == "EH":
            print("")

            print(
                "----",
                (
                    "Derived cosmology parameters for Eisenstein and Hu"
                    " transfer function "
                ).ljust(70, "-"),
            )
            print()
            print(
                "  {:45s}: {}".format(
                    "k_Silk (Silk damping scale [Mpc-1])", self._params._k_Silk
                )
            )

        if self._params.pk_type in ("BBKS", "BBKS_CCL"):
            print(
                "----",
                "Derived cosmology parameters for BBKS transfer function ".ljust(
                    70, "-"
                ),
            )

            print()
            print(
                "  {:45s}: {}".format(
                    "gamma (Gamma Sugiyama [h Mpc-1])", self._params.gamma
                )
            )
