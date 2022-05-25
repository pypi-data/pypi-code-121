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
import scipy

from PyCosmo.PerturbationBase import NonLinearPerturbationBase


class NonLinearPerturbationHaloFit(NonLinearPerturbationBase):

    """
    The class computes the non-linear matter power spectrum, :math:`P_{nl}(k)`,
    with a choice of analytic fitting funtions.

    .. Warning ::
        NonLinearPerturbationHalofit not supported by the Boltzmann solver yet.
        Calling any function from this module while using the Boltzmann solver (pk_type
        = 'boltz') will return **AttributeError: 'NoneType' object has no attribute
        'function'**
    """

    def __init__(self, cosmo):
        self._params = cosmo.params
        self._background = cosmo.background
        self._lin_pert = cosmo.lin_pert

    def k_nl(self, a):
        r"""Computes the non-linear wave number :math:`k_{nl}` as a function of the
        scale factor a.

        :param a: scale factor [1]
        :return: k_nl: non-linear wave number [:math:`\mathrm{Mpc}^{-1}`]
        """
        logk_ran = [-3.0, 2.0]
        k = np.logspace(logk_ran[0], logk_ran[1], num=1000)
        aa = np.atleast_1d(a)
        k_nl = np.zeros(len(aa))
        for i in range(len(aa)):
            # Delta^2=k ** 3*P(k)/(2 pi ** 2)
            del2 = self._lin_pert.powerspec_a_k(aa[i], k)[0] * k**3 / 2.0 / np.pi**2
            # k_nl defined such that Delta^2(k_nl)=1
            k_nl[i] = np.interp(1.0, del2, k)
            if k_nl[i] < 10 ** logk_ran[0] or k_nl[i] > 10 ** logk_ran[1]:
                print("k_nl: warning: k_nl outside of search k range")
        return k_nl

    def max_redshift(self, k):
        """computes max redshift for which this model is applicable.

        :param k: wavenumber k, might be needed for some underlying linear perturbation
                  models.  [:math:`h Mpc^{-1}`]
        :returns: redshift
        """
        return self._lin_pert.max_redshift(k)

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        """
        Returns the nonlinear matter power spectrum using a choice of fitting functions.
        Currently both the *Halofit* fitting function and its revision by
        `Takahashi et al., 2012 <https://arxiv.org/abs/1208.2701>`_ are supported.
        Those can be selected using the *set function*:

        .. code-block:: python

            cosmo.set(pk_nonlin_type = option)

        where *option* can be one the following keywords:

        - ``halofit`` (default) for
           `Smith et al., 2003, MNRAS, 341, 1311
            <https://arxiv.org/abs/astro-ph/0207664>`_
        - ``rev_halofit`` for revision by
            `Takahashi et al., 2012, ApJ, 761, 152 <https://arxiv.org/abs/1208.2701>`_

        After selecting the fitting function, the non-linear matter power spectrum,
        :math:`P_{nl}(k)`, can be computed as follows:

        .. code-block:: python

            cosmo.nonlin_pert.powerspec_a_k(a,k)

        :param a: scale factor [1]
        :param k: wavenumber :math:`[Mpc^{-1}]`
        :return: Nonlinear matter power spectrum, :math:`P_{nl}(k)`, in :math:`[Mpc^3]`.
        """

        if self._params.pk_nonlin_type in ("halofit", "rev_halofit"):
            return self._powerspec_nonlin_halofit_a_k(
                a, k, self._params.pk_nonlin_type, diag_only
            )
        raise NotImplementedError(
            "{} not implemented yet".format(self._params.pk_nonlin_type)
        )

    def _interp_k_sig(self, a):
        """Creates an interpolant to the k_sig-redshift relation in order to speed up
        the calculation of the nonlinear matter power spectrum.
        : param a: scale factor [1]
        : return: nonlinear scale k_sig(a) needed to compute nonlinear matter
                  power spectrum [:math:`Mpc^{-1}`]
        """

        a = np.atleast_1d(a)

        if not hasattr(self, "halofit_params_interp"):
            a_temp = np.logspace(-4, 0, 1000)
            # restrict to valid a values for approximate lin pert models:

            # Need to precompute ksig with a fine k grid for each input scale
            # factor a
            k_temp = np.logspace(-4, 4, 1000)

            a_limit = 1 / (1 + self.max_redshift(k_temp))
            a_temp = a_temp[a_temp >= a_limit]
            pklin_temp = self._lin_pert.powerspec_a_k(a=a_temp, k=k_temp)
            Dlin_temp = self._pk_to_D(
                pklin_temp, np.reshape(k_temp, (k_temp.shape[0], 1))
            )

            k_sig_interp = np.zeros_like(a_temp)
            np3_interp = np.zeros_like(a_temp)
            C_interp = np.zeros_like(a_temp)
            for i, ai in enumerate(a_temp):
                k_sig_interp[i], np3_interp[i], C_interp[i] = self._k_sig(
                    Dlin_temp[:, i], ai, k_temp
                )

            self.halofit_params_interp = np.vstack(
                (a_temp, k_sig_interp, np3_interp, C_interp)
            )

        k_sig = np.interp(
            a,
            self.halofit_params_interp[0, :],
            self.halofit_params_interp[1, :],
            left=np.nan,
            right=np.nan,
        )
        np3 = np.interp(
            a,
            self.halofit_params_interp[0, :],
            self.halofit_params_interp[2, :],
            left=np.nan,
            right=np.nan,
        )
        C = np.interp(
            a,
            self.halofit_params_interp[0, :],
            self.halofit_params_interp[3, :],
            left=np.nan,
            right=np.nan,
        )

        return k_sig, np3, C

    def _powerspec_nonlin_halofit_a_k(self, a, k, model, diag_only):
        """Returns the halofit nonlinear matter power spectrum per k as defined in
        Smith et al., 2003, MNRAS, 341, 1311."""

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        lenk = k.shape[0]
        lena = a.shape[0]

        if diag_only:
            assert lenk == lena
            pklin_temp = self._lin_pert.powerspec_a_k(a=a, k=k, diag_only=True)
            Dlin_temp = self._pk_to_D(pklin_temp, k)
            k_sig, np3, C = self._interp_k_sig(a)
            D_halofit = self._D_nonlin_halofit(Dlin_temp, k, k_sig, np3, C, a, model)
            pk_halofit = self._D_to_pk(D_halofit, k)
            return pk_halofit

        # TODO Need to decide how the nonlinear power spectrum should be
        # computed

        pklin_temp = self._lin_pert.powerspec_a_k(a=a, k=k)
        Dlin_temp = self._pk_to_D(pklin_temp, k[:, None])
        k_sig, np3, C = self._interp_k_sig(a)
        k_arr = np.tile(k, lena)
        k_arr = k_arr.reshape((-1, lenk)).T
        D_halofit = self._D_nonlin_halofit(Dlin_temp, k_arr, k_sig, np3, C, a, model)

        pk_halofit = self._D_to_pk(D_halofit, np.reshape(k, (lenk, 1)))

        if diag_only:
            return np.diag(pk_halofit)
        return pk_halofit

    def _pk_to_D(self, pk, k):
        """Returns the matter power spectrum per unit lnk from an
        input matter power spectrum per unit k."""

        return k**3 * pk / (2 * np.pi**2)

    def _D_to_pk(self, D, k):
        """Returns the matter power spectrum per unit k from an
        input matter power spectrum per unit lnk."""

        return (2 * np.pi**2) * D / k**3

    def _k_sig(self, Dlin, a, k):
        """Computes the scale k_sig which satisfies sig^2(1/ksig) = 1 where
        sig^2(R) = int dlnk Dlin Wgauss(kR) ** 2 as defined in Eq. 54 of
        Smith et al., 2003, MNRAS, 341, 1311"""

        if a > 0.3:
            if self._params.pk_norm >= 0.65 and self._params.pk_norm <= 1.2:
                logkmin = -1
                logkmax = 2
                nk = 300
            elif self._params.pk_norm < 0.65:
                logkmin = -1
                logkmax = 6
                nk = 200
            else:
                logkmin = -2
                logkmax = 4
                nk = 110
        # 2nd case: redshift larger than 2.3
        else:
            # Redshift smaller than five
            if a > 0.166:
                if self._params.pk_norm >= 0.6:
                    logkmin = -1.0
                    logkmax = 4
                    nk = 600
                else:
                    logkmin = 0.0
                    logkmax = 7
                    nk = 1000
            elif a <= 0.166 and a > 0.125:
                logkmin = -1
                logkmax = 7
                nk = 600
            else:
                logkmin = -1
                logkmax = 7
                nk = 200

        kseek = np.logspace(logkmin, logkmax, nk)

        sig2gauss = np.trapz(
            np.exp(-np.outer(1 / kseek, k) ** 2) * Dlin / k, x=k, axis=1
        )

        ksig = np.interp(1.0, sig2gauss, kseek)

        # If the ksig determination goes out of bounds or sig^2(ksig^-1) is not strictly
        # increasing # we return ksig = nan
        if any([ksig == kseek[-1], ksig == kseek[0], np.any(np.diff(sig2gauss) <= 0)]):
            ksig = np.nan

        # assert np.abs(sig-1.0) <= 10 ** (-6), \
        # 'The determination of k_sig failed to reach the required accuracy of 10^-6.\
        # sig-1.0 = %d' %(np.abs(sig-1.0))

        y = k / ksig
        ysq = y**2
        # Effective index, equation (C7)
        # n = -3 - dlnsig^2/dlnR
        #   = -3 + 2 int dlnk Dlin (k/ksig)^2 Wgauss(k/ksig) ** 2
        np3 = 2.0 * np.trapz(ysq * np.exp(-ysq) * Dlin / k, x=k)
        # Spectral curvature, equation (C8)
        # C = - d^2lnsig^2/dlnR^2
        #   = 2(n+3) + (n+3)^2 - 4 int dlnk Dlin (k/ksig)^4 Wgauss(k/ksig) ** 2
        C = (
            (np3 + 1.0) ** 2
            - 1.0
            - 4.0 * np.trapz(ysq**2 * np.exp(-ysq) * Dlin / k, x=k)
        )

        return ksig, np3, C

    def _D_nonlin_halofit(self, Dlin, k, ksig, np3, C, a=1.0, model="halofit"):
        """Returns the halofit nonlinear matter power spectrum per lnk
        starting from the desired linear matter power spectrum.
        If model == 0 it returns the nonlinear matter power spectrum as defined in
        Smith et al., 2003, MNRAS, 341, 1311.
        Note: all equations are defined in Appendix C of Smith et al.,
        2003, MNRAS, 341, 1311
        If model == 1 it returns the nonlinear matter power spectrum as defined in
        Takahashi et al., 2012, ApJ, 761, 152
        Note: all equations are defined in the Appendix of Takahashi et al.,
        2012, ApJ, 761, 152"""

        # Determine the fractional matter density at the redshift of interest
        omega_m_z = self._background._omega_m_a(a=a)

        # Dimensionless wavenumber, below Eq. (C2)
        y = k / ksig
        ysq = y**2
        # Effective index, equation (C7)
        # n = -3 - dlnsig^2/dlnR
        #   = -3 + 2 int dlnk Dlin (k/ksig)^2 Wgauss(k/ksig) ** 2
        # np3 = 2*np.trapz(ysq*np.exp(-ysq)*Dlin/k,x=k)
        n = np3 - 3.0
        n2 = n**2
        n3 = n2 * n
        n4 = n2**2
        # Spectral curvature, equation (C8)
        # C = - d^2lnsig^2/dlnR^2
        #   = 2(n+3) + (n+3)^2 - 4 int dlnk Dlin (k/ksig)^4 Wgauss(k/ksig) ** 2
        # C = (np3+1) ** 2 - 1 - 4*np.trapz(ysq ** 2*np.exp(-ysq)*Dlin/k,x=k)

        # Coefficients used in the fitting function - this is the only difference
        # between # Smith et al, 2003 and Takahashi et al., 2012
        # Parameters from Smith et al, 2003 (model='halofit') or Takahashi et al. 2012
        # (model='takahashi')
        # Equations (C9) - (C16) of Smith et al., 2003
        if model == "halofit":
            lga = (
                1.4861
                + 1.8369 * n
                + 1.6762 * n2
                + 0.7940 * n3
                + 0.1670 * n4
                - 0.6206 * C
            )
            lgb = 0.9463 + 0.9466 * n + 0.3084 * n2 - 0.9400 * C
            lgc = -0.2807 + 0.6669 * n + 0.3214 * n2 - 0.0793 * C
            alpha = 1.3884 + 0.3700 * n - 0.1452 * n2
            beta = 0.8291 + 0.9854 * n + 0.3401 * n2
            gamma = 0.8649 + 0.2989 * n + 0.1631 * C
            mu = 10 ** (-3.5442 + 0.1908 * n)
            lgnu = 0.9589 + 1.2857 * n
        elif model == "rev_halofit":
            # Equations (A6) - (A13) of Takahashi et al., 2012
            omega_l_z = self._background._omega_l_a(a=a)
            lga = (
                1.5222
                + 2.8553 * n
                + 2.3706 * n2
                + 0.9903 * n3
                + 0.2250 * n4
                - 0.6038 * C
                + 0.1749 * omega_l_z * (1 + self._params.w0)
            )
            lgb = (
                -0.5642
                + 0.5864 * n
                + 0.5716 * n2
                - 1.5474 * C
                + 0.2279 * omega_l_z * (1 + self._params.w0)
            )
            lgc = 0.3698 + 2.0404 * n + 0.8161 * n2 + 0.5869 * C
            alpha = np.abs(6.0835 + 1.3373 * n - 0.1959 * n2 - 5.5274 * C)
            beta = (
                2.0379
                - 0.7354 * n
                + 0.3157 * n2
                + 1.2490 * n3
                + 0.3980 * n4
                - 0.1682 * C
            )
            gamma = 0.1971 - 0.0843 * n + 0.8460 * C
            mu = 0.0
            lgnu = 5.2105 + 3.6902 * n
        else:
            raise NotImplementedError(
                "non linear model {} not implemented".format(model)
            )

        a_hf = 10**lga
        b = 10**lgb
        c = 10**lgc
        nu = 10**lgnu

        # omega_m_z dependent functions
        # 1st case: Matter dominated universe
        if self._params.omega_m == 1.0:
            f1 = 1.0
            f2 = 1.0
            f3 = 1.0
        # 2nd case: universe is not matter dominated, interpolate linearily between
        # dark energy w and curvature with w_eff = -1/3
        else:
            w_z = self._background._w_a(a=a)

            f1a = omega_m_z**-0.0732
            f2a = omega_m_z**-0.1423
            f3a = omega_m_z**0.0725
            f1b = omega_m_z**-0.0307
            f2b = omega_m_z**-0.0585
            f3b = omega_m_z**0.0743

            frac1 = self._params.omega_l / (self._params.omega_l + self._params.omega_k)
            we = frac1 * w_z + 1.0 / 3.0 * (1.0 - frac1)
            frac2 = -1.0 * ((3.0 * we) + 1.0) / 2.0

            f1 = frac2 * f1b + (1 - frac2) * f1a
            f2 = frac2 * f2b + (1 - frac2) * f2a
            f3 = frac2 * f3b + (1 - frac2) * f3a

        # The quasi-linear term
        # Equation (C2)
        DQ = (
            Dlin
            * np.exp(-0.25 * y - 0.125 * ysq)
            * (1 + Dlin) ** beta
            / (1 + alpha * Dlin)
        )

        # The halo term
        # Equations (C3) - (C4)
        DH = (
            a_hf
            * y ** (2 + 3 * f1)
            / (ysq + mu * y + nu)
            / (1 + b * y**f2 + (c * f3 * y) ** (3 - gamma))
        )

        return DQ + DH

    # The set of fucntions useful to comupte the One-Halo and Two-Halo terms
    # in Mead follow here

    def _sigma_v(self, k, Dlin):
        """
        :param a: scale factor
        :param k: wavenumber [Mpc^-1]
        :param Dlin: P(k) linear-theory matter power spectrum P(k) [Mpc^3]
        :return: 1D linear displacement variance, as defined in eq.4 in Mead et al, 2015
        """
        integr = 1.0 / 3 * np.trapz(Dlin / (k**3), x=k, axis=1)
        sigmav = np.sqrt(integr)
        return np.sqrt(sigmav)

    def _sigma_d_100(self, k, Dlin):
        """
        :param a: scale factor
        :param k: wavenumber [Mpc^-1]
        :param Dlin: P(k) linear-theory matter power spectrum P(k) [Mpc^3]
        :return: 1D linear displacement variance, as defined in eq.4 in Mead et al, 2016
        """
        k = np.atleast_1d(k)
        R = 100.0 / self._params.h
        T = 3 / ((k * R) ** 3) * (np.sin(k * R) - np.cos(k * R))
        # T = self.T(k * R)
        integr = 1.0 / 3 * np.trapz((Dlin / (k**3)) * (T**2), x=k, axis=1)
        sigma_d100 = np.sqrt(integr)
        return sigma_d100

    def _sigma8(self, a, k, Dlin):
        """
        Compute sigma8, the rms density contrast fluctuation smoothed with a top hat of
        radius 8 h^-1 Mpc at redshift z.
        :param a: scale factor
        :param k: wavenumber [Mpc^-1]
        :param Dlin: P(k) linear-theory matter power spectrum P(k) [Mpc^3]
        :return sig8z: sigma8 at the desired redshift [1]
        """
        R = 8.0 / self._params.h  # smoothing radius [Mpc]
        lnk = np.log(k)
        w = (
            3 / ((k * R) ** 3) * (np.sin(k * R) - np.cos(k * R))
        )  # top hat window function
        res = np.trapz(k**3 * Dlin[0] * w**2, lnk)
        sig8z = np.sqrt(1.0 / (2.0 * np.pi**2) * res)

        return sig8z

    def _windowf(self, k, r_v, c):
        """
        :param r_v: virial radius
        :param c: concentration parameter
        :return: Fourier Transform of the halo density profile
        """
        k = np.atleast_1d(k)
        # Normalised mass of a halo of concentration c
        f_c = np.log(1 + c) - c / (1 + c)
        k_s = k * r_v / c

        Si1, Ci1 = scipy.special.sici(k_s * (1 + c))
        Si2, Ci2 = scipy.special.sici(k_s)
        W = (
            (Ci1 - Ci2) * np.cos(k_s)
            + (Si1 - Si2) * np.sin(k_s)
            - np.sin(c * k_s) / (k_s * (1 + c))
        ) / f_c
        return W

    def _rho_critic(self):
        # Newton's gravitational constant as in Mo, Bosch & White "Galaxy
        # Formation and Evolution" (2010)
        G = 4.299e-9
        rho = 3 * self._params.H0**2 / (8 * np.pi * G)
        return rho
