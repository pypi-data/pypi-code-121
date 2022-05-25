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


import numba
import numpy as np
from scipy import special

from PyCosmo.cython.halo_integral import _integral_halo as cython_integral_halo
from PyCosmo.PerturbationBase import NonLinearPerturbationBase
from PyCosmo.TheoryPredTables import TheoryPredTables

from ._scipy_utils import interp1d


"""
based on:

    Halo Model
    by Lukas Hergt, Institute for Astronomy, ETH Zurich


rewrite by:

    Uwe Schmitt
    Scientific IT Services
    ETH Zurich
    schmittu@ethz.ch
    March 2018

"""


@numba.jit(numba.float64[:](numba.float64[:]))
def fft_top_hat(x):  # pragma: no cover
    """
    Fourier transform of 3D spherical top hat.

    :param x: dimensionless parameter (usually k r)
    :return t: Fourier transform of a 3D spherical top hat.
    """

    cutoff = 1e-8
    # x values below thresh will yield a result abs smaller than cutoff:
    thresh = np.sqrt(6 / cutoff)

    t = np.zeros(len(x))

    for i, y in enumerate(x):

        if y > thresh:
            continue

        elif y > 1e-2:
            t[i] = 3.0 * (np.sin(y) - y * np.cos(y)) / y**3.0
        else:
            t[i] = 1.0 - y**2.0 / 10.0 + y**4.0 / 280.0

    return t


def _u_km_slow(k, a, c, rv_mpc, nu_range, eta):
    """
    Fourier transform u(k,M) of the NFW profile, normed such that the integrated mass
    equals one.

    :param k: wavenumber [Mpc^-1]
    :param m_msun: halo mass in solar masses [Msun]
    :param a: scale factor
    :return ukm: Fourier Transform u(k,M) of the NFW profile [1]
    """

    k = k[None, :, None] * nu_range[:, None, None] ** eta[None, None, :]
    nm, nk, __ = k.shape
    na = len(a)

    c = np.atleast_2d(c).T[:, None, :]
    rv_mpc = np.atleast_2d(rv_mpc).T[:, None, :]
    assert rv_mpc.shape == (nm, 1, na)
    assert c.shape == (nm, 1, na)

    rs_mpc = rv_mpc / c
    normalisation = np.log(1.0 + c) - c / (1.0 + c)

    krs = k * rs_mpc
    assert krs.shape == (nm, nk, na)

    ci_krs = c * krs
    ci_plus_1_krs = (1 + c) * krs
    si_k, ci_k = special.sici(krs)
    si_ck, ci_ck = special.sici(ci_plus_1_krs)

    term1 = np.cos(krs) * (ci_ck - ci_k)
    term2 = np.sin(krs) * (si_ck - si_k)
    term3 = -np.sin(ci_krs) / ci_plus_1_krs

    return (term1 + term2 + term3) / normalisation


def integral_halo(k, m_msun, nu_range, rv_mpc, c, a, f, eta):

    nufuncs = m_msun[:, None, :].T * nu_range[:, None, None] * f[:, None, None]
    u_km = _u_km_slow(k, a, c, rv_mpc, nu_range, eta)
    integrand_1halo = nufuncs * u_km**2.0
    integral_1halo = np.trapz(integrand_1halo, np.log(nu_range), axis=0)
    return integral_1halo


class NonLinearPerturbationMead(NonLinearPerturbationBase):
    r"""
    The class incorporates the implementation of the :math:`\texttt{HMCode}` as
    described in
    `Mead et al. 2015 <https://arxiv.org/abs/1505.07833>`_
    and `Mead et al. 2016 <https://arxiv.org/abs/1602.02154>`_ .

    .. Warning ::
        NonLinearPerturbationMead not supported by the Boltzmann solver yet.  Calling
        any function from this module while using the Boltzmann solver (pk_type =
        'boltz') will return **AttributeError: 'NoneType' object has no attribute
        'function'**
    """

    def __init__(self, cosmo):
        self._params = cosmo.params
        self._background = cosmo.background
        self._lin_pert = cosmo.lin_pert
        self._tables = TheoryPredTables(self._lin_pert)

        self._enrich_params()
        self._setup_interpolation_functions()

    def _enrich_params(self):

        # First term. eta0, of the Halo bloating parameter eta
        self._params.eta0 = 0.98 - 0.12 * self._params.A_mead

        # Newton's gravitational constant as in Mo, Bosch & White, 2010
        self._params.G_mead = 4.299e-9

        # Parameters used for the mass function, according to Shets & Tormen, 1999 (ST)
        # or Tinker et al., 2010 (Ti)
        if self._params.multiplicity_fnct == "ST":
            # Sheth & Tormen, 'Large-scale bias and the peak background split', 1999
            self._params.mf_aa = 0.3222
            self._params.mf_a = 0.707
            self._params.mf_p = 0.3

        elif self._params.multiplicity_fnct == "TI":
            # Tinker et al., 'Large-scale bias of dark matter halos', 2010
            self._params.mf_aa = 0.368
            self._params.mf_a = -0.729
            self._params.mf_b = 0.589
            self._params.mf_c = 0.864
            self._params.mf_n = -0.243

        self._params.rho_crit_Msun_iMpc3 = (
            3 * self._params.H0**2 / (8 * np.pi * self._params.G_mead)
        )
        self._params.rho_matter_Msun_iMpc3 = (
            self._params.rho_crit_Msun_iMpc3 * self._params.omega_m
        )

        self._params.bins = 1000

    def _eta(self, a):
        sigma8_a = self.sigma8_a(a)
        return self._params.eta0 - 0.3 * sigma8_a

    def _setup_interpolation_functions(self, a0=0.5):
        """
        Set up derived parameters for scale factor a. The order is slightly weird but
        this is due to the fact that the lookup tables need delta_c and n needs the
        lookup tables.
        :param a: scale factor a
        :param k: wavenumber k
        :return:
        """

        bins = self._params.bins
        assert bins >= 1000, "bins should be >=1000"

        m_grid = 10 ** np.linspace(-250, 20, bins - 1)
        s_grid_0 = self._sigma([m_grid], a0).flatten()

        assert np.all(np.diff(s_grid_0) <= 0), "s-array not monotone falling"

        self.sigma_a0_function = interp1d(
            np.log(m_grid + 1e-300),
            s_grid_0,
            kind="quadratic",
            fill_value="extrapolate",
        )

        if bins < 10000:
            m_vec = np.append([1e-300], 10 ** np.linspace(-250, 20, 9999))
            s_vec = self.sigma_a0_function(np.log(m_vec + 1e-300))
        else:
            m_vec = m_grid
            s_vec = s_grid_0

        self.delta_c_a0 = delta_c_a0 = self.delta_c(a0)
        self.nu0 = nu0 = delta_c_a0 / s_vec

        self.growth_a0 = self._tables.growth_tab_a(a=a0)

        self.nu0_to_mass = interp1d(nu0, m_vec, kind="linear", fill_value="extrapolate")

    def nu2mass(self, nu, a):
        r"""
        Extracts the halo mass from Eq.(17) in
        `Mead et al., 2015 <https://arxiv.org/abs/1505.07833>`_,
        :math:`\nu = \delta_c / \sigma`, by converting the :math:`\nu`-array
        into a mass-array by backwards interpolation.

        :param nu: :math:`\nu`-array as in :math:`\nu = \delta_c / \sigma` [1]
        :return: Mass in solar masses [Msun].
        """

        nu = np.atleast_1d(nu)
        a = np.atleast_1d(a)

        delta_c_a = self.delta_c(a)
        nu0 = (
            nu
            * (
                self._tables.growth_tab_a(a=a)
                / self.growth_a0
                * self.delta_c_a0
                / delta_c_a
            )[:, None]
        )
        mask = nu0 < min(self.nu0)
        nu0[mask] = min(self.nu0)
        masses = self.nu0_to_mass(nu0)
        masses[mask] = 0
        return masses

    def _alpha(self, a):
        n = self.neff(a)
        alpha = 3.24 * 1.85**n
        alpha[alpha > 2] = 2
        alpha[alpha < 0.5] = 0.5
        return alpha

    def delta_c(self, a):
        r"""
        Computation of the linear collapse threshold, :math:`\delta_c`.

        Following `Mead et al., 2015, <https://arxiv.org/abs/1505.07833>`_,
        :math:`\delta_c` is treated as a fitting parameter (read its fitted value in
        Table 2 of the paper). The current implementation in :math:`\textsf{PyCosmo}`
        follows the updated formula reported in Eq.(8) of
        `Mead et al., 2016, <https://arxiv.org/abs/1602.02154>`_,
        where the original prescription from 2015 is augmented by the fitting formula
        proposed in Eq. C28 of
        `Nakamura & Suto, 1997 <https://arxiv.org/abs/astro-ph/9612074>`_.

        :param a: scale factor [no dimensions]
        :return: Linear collapse threshold, :math:`\delta_c`.
        """

        fac2 = 1.59 + 0.0314 * np.log(self.sigma8_a(a))
        return (1.0 + 0.0123 * np.log10(self._background._omega_m_a(a=a))) * fac2

    def _pk_to_D(self, pk, k):
        """
        Compute the matter power spectrum per unit log k from an input matter power
        spectrum per unit k.
        :param pk: matter power spectrum pk
        :param k: wave vector k
        :return D: dimensionless matter power spectrum variance per unit log
        """
        # TODO: move this method to base class LinearPerbutabionBase

        nk, na = pk.shape
        assert k.shape == (nk,)

        D = k[:, None] ** 3 * pk / (2 * np.pi**2)

        return D

    def mass2radius(self, m_msun):
        """
        Converts mass of a sphere in solar masses [Msun] to corresponding radius in
        [Mpc], assuming homogeneous density corresponding to the critical matter density
        of the universe (redshift z=0).

        :param m_msun: mass of sphere in solar masses [Msun]
        :return: Radius of the sphere in [Mpc].
        """

        radius = (
            3.0 * m_msun / (4.0 * np.pi * self._params.rho_matter_Msun_iMpc3)
        ) ** (1.0 / 3.0)

        return radius

    def radius2mass(self, r_mpc):
        """
        Converts radius of a sphere in [Mpc] to corresponding mass in solar masses
        [Msun], assuming homogeneous density corresponding to the critical matter
        density of the universe (redshift z=0).

        :param r_mpc: radius of sphere [Mpc]
        :return: Mass of sphere in solar masses [Msun].
        """

        mass = 4.0 / 3.0 * np.pi * r_mpc**3.0 * self._params.rho_matter_Msun_iMpc3

        return mass

    def rvir(self, mvir_msun, a):
        # TODO: Extend this beyond flat cosmologies?
        """
        Calculates the virial radius corresponding to a dark matter halo of mass m_msun
        in a flat cosmology. See
        `Bryan & Norman, 1998 <https://arxiv.org/abs/astro-ph/9710107>`_
        for more details.

        :param mvir_msun: Halo mass in solar masses [Msun]
        :return: Virial radius in :math:`[Mpc]`.
        """

        delta_v = 418.0 * self._background._omega_m_a(a=a) ** (-0.352)

        rvir3 = (3.0 * mvir_msun) / (
            4.0 * np.pi * self._params.rho_matter_Msun_iMpc3 * delta_v[:, None]
        )

        rvir_mpc = rvir3 ** (1.0 / 3.0)

        return rvir_mpc

    def T(self, x):
        r"""
        Computes the Fourier Transform of a 3D spherical top-hat function.

        :param x: dimensionless parameter (usually equal to :math:`kr`) [1]
        :return: Fourier Transform of a 3D spherical top-hat function.
        """

        orig_shape = x.shape
        x_flat = np.ravel(x)
        t = fft_top_hat(x_flat)
        t = t.reshape(orig_shape)

        return t

    def T_deriv(self, x):
        r"""
        Analytical computation of the derivative of the Fourier Transform of a 3D
        spherical top-hat function.

        :param x: dimensionless parameter (usually equal to :math:`kr`) [1]
        :return: Derivative of the Fourier Transform of a 3D spherical top-hat function.
        """

        x = np.atleast_1d(x)
        return np.where(
            x > 1e-2,
            3.0 / x**4 * (x**2 * np.sin(x) - 3.0 * np.sin(x) + 3.0 * x * np.cos(x)),
            -x / 5.0 + x**3 / 70.0,
        )

    def neff(self, a):
        r"""
        Calculates the effective spectral index of the linear power spectrum at the
        collapse scale, according to the implementation in the HMCode.

        :param a: scale factor [1]
        :return: Effective spectral index of the linear power spectrum, :math:`n_{eff}`,
                 at the collapse scale.
        """

        a = np.atleast_1d(a)

        # Calculate ksig as nu(1/ksig) = 1
        m = self.nu2mass([1.0], a)
        # Calculate rsig
        rsig = self.mass2radius(m)

        assert rsig.shape == (len(a), 1)
        # Calculate ksig
        ksig = 1.0 / rsig

        # Calculate the linear power spectrum
        k_temp = np.logspace(-4, 4, 5000)
        pklin = self._lin_pert.powerspec_a_k(k=k_temp, a=a)
        Dlin = self._pk_to_D(pklin, k_temp)
        # Calculate the top hat window function and its derivative

        Tksig = self.T(k_temp / ksig).T
        assert Tksig.shape == (len(k_temp), len(a))

        Tksig_deriv = self.T_deriv(k_temp / ksig).T
        assert Tksig.shape == (len(k_temp), len(a))

        # Effective index
        # n = -3 - dlnsig^2/dlnR|R=1/ksig
        # The division by sigma^2(1/ksig) is needed because sigma^2(1/ksig) is not 1

        i1 = np.trapz(Tksig * Tksig_deriv * Dlin, x=k_temp, axis=0)
        i2 = np.trapz(
            self.T(1.0 / ksig * k_temp).T ** 2 * Dlin / k_temp[:, None],
            x=k_temp,
            axis=0,
        )
        np3 = -2.0 / ksig.flatten() * i1 / i2

        neff = np3 - 3.0
        # neff=-2.00168848
        return neff

    def sigma_v_a(self, a):
        r"""
        Computes :math:`\sigma^2_V(a)` as defined in Eq. (22)
        of `Mead et al, 2015 <https://arxiv.org/abs/1505.07833>`_ .

        :param a: scale factor [1]
        :return: :math:`\sigma^2_v(a)` at the desired scale factor.
        """

        a = np.atleast_1d(a)

        k = np.logspace(-6, 4.0, num=5000)  # grid of wavenumber k [Mpc^-1]
        pklin = self._lin_pert.powerspec_a_k(k=k, a=a)
        Dlin = self._pk_to_D(pklin, k)

        res = np.trapz(Dlin / k[:, None] ** 3, k, axis=0)
        sigv = np.sqrt(res / 3.0)
        assert sigv.shape == (len(a),)
        return sigv

    def sigma_d(self, a, R=100.0):
        r"""
        Computes :math:`\sigma^2_D(a)` as defined in Eq. B5 of
        `Mead et al, 2015 <https://arxiv.org/abs/1505.07833>`_

        :param a: scale factor [1]
        :return: :math:`\sigma^2_D(a)` at the desired scale factor.
        """
        a = np.atleast_1d(a)
        R = R / self._params.h
        k = np.logspace(-6, 4.0, num=5000)  # grid of wavenumber k [Mpc^-1]
        pklin = self._lin_pert.powerspec_a_k(k=k, a=a)
        Dlin = self._pk_to_D(pklin, k)
        T = self.T(k * R)

        res = np.trapz(T[:, None] ** 2 * Dlin / k[:, None] ** 3, x=k, axis=0)

        sigv = np.sqrt(res / 3.0)
        return sigv

    def sigma8_a(self, a):
        r"""
        Compute :math:`\sigma_8`, the rms density contrast fluctuation, smoothed with a
        top hat of radius 8 :math:`h^{-1}\mathrm{Mpc}` at scale factor a.

        :param a: scale factor [1]
        :return: :math:`\sigma_8` at the desired scale factor.
        """

        a = np.atleast_1d(a)
        r = 8.0 / self._params.h  # smoothing radius [Mpc]
        k = np.logspace(-5.0, 2.0, num=5000)  # grid of wavenumber k [Mpc^-1]
        lnk = np.log(k)

        w = self.T(k * r)  # top hat window function
        pk = self._lin_pert.powerspec_a_k(a=a, k=k)
        res = np.trapz(k[:, None] ** 3 * pk * w[:, None] ** 2, lnk, axis=0)

        sig8z = np.sqrt(1.0 / (2.0 * np.pi**2) * res)
        return sig8z

    def _calc_sigma_integral(self, k, m_msun, a):
        r"""
        Calculate the unnormed sigma^2.
        :param k: wavelength array over which the integration is performed [Mpc^-1]
        :param m_msun: mass in solar masses at which sigma^2 is evaluated [Msun]
        :param a: scale factor
        :return: unnormed sigma^2 [dimensionless]
        """

        # here: first dimension: k, second msun, third a

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        m_msun = np.atleast_2d(m_msun)

        nk = k.shape[0]
        na = a.shape[0]
        nm = m_msun.shape[1]
        assert m_msun.shape[0] == na

        ps = self._lin_pert.powerspec_a_k(a=a, k=k)[:, None, :]

        r_mpc = np.atleast_2d(self.mass2radius(m_msun=m_msun)).T[None, :, :]
        assert r_mpc.shape == (1, nm, na)

        t = self.T(x=r_mpc * k[:, None, None])
        assert t.shape == (nk, nm, na)
        integrand_mpc = ps * t**2.0 * k[:, None, None] ** 3.0

        integral = np.trapz(integrand_mpc, np.log(k), axis=0)

        return integral.flatten()

    def _sigma(self, m_msun, a):
        r"""computes sigma for a single a"""

        a = np.atleast_1d(a)
        assert len(a) == 1

        nk = self._params.npoints_k
        # Wavenumber k [Mpc^1] to integrate over
        k = np.append([1e-100], 10 ** np.linspace(-10, 100, nk))
        # This deals with missing factors of 2 pi^2 - could also be omitted!
        m_msun_8 = self.radius2mass(8.0 / self._params.h)
        sigma8norm = np.sqrt(self._calc_sigma_integral(k=k, m_msun=m_msun_8, a=a))

        # We need to normalise with the value of sigma8 at the desired redshift
        s8z = self.sigma8_a(a=a)
        sigma = np.sqrt(self._calc_sigma_integral(k=k, m_msun=m_msun, a=a))

        return sigma / sigma8norm * s8z

    # sigma -> _sigma_m_a, can I move this to HaloFitBaseClass API ?

    def sigma(self, m_msun, a):
        r"""
        Calculates :math:`\sigma(M, a)`, the RMS of the density field at a given mass.

        :param m_msun: mass in solar masses at which sigma is evaluated [Msun]
        :param a: scale factor [1]
        :return: :math:`\sigma(M, a)` as the RMS of the density field.
        """

        a = np.atleast_1d(a)
        m_msun = np.atleast_1d(m_msun)
        if m_msun.ndim == 1:
            m_msun = np.atleast_2d([m_msun] * len(a))
        assert m_msun.shape[0] == a.shape[0]

        # we make use of the fact that sigma(a) / growth(a) == sigma(a') / growth(a').
        # so for a particular m_msun and a vector a we only need to compute sigma for
        # the first entry of a, and all other sigma values can be computed by scaling.
        sigma0s = []
        for ai, msi in zip(a, m_msun):
            sigma0 = self.sigma_a0_function(np.log(msi + 1e-300)) / self.growth_a0
            sigma0s.append(sigma0)
        growth_a = self._tables.growth_tab_a(a=a)
        return (growth_a[:, None] * np.vstack(sigma0s)).T

    def f(self, nu):
        r"""
        Multiplicity function :math:`f(\nu)` as it appears in the calculation of the
        Halo Mass Function.  The available fitting functions are
        `Press & Schechter,
        1974 <https://ui.adsabs.harvard.edu/abs/1974ApJ...187..425P/abstract>`_,
        `Sheth & Tormen, 1999 <https://arxiv.org/abs/astro-ph/9901122>`_ ,
        and `Tinker et al., 2010 <https://arxiv.org/abs/1001.3162>`_ .

        :param nu: array of :math:`\nu` values as in :math:`\nu = \delta_c / \sigma(M)`\
            (see eq. 17 in `Mead et al., 2015 <https://arxiv.org/abs/1505.07833>`_)
        :return: Multiplicity function :math:`f(\nu)` .

        Example of setting the multiplicity function:

        .. code-block:: python

            cosmo.set(multiplicity_fnct = option)

        where *option* can be 'PS' for *Press & Schechter (1974)*, 'ST' for *Sheth &
        Tormen (1999)* or 'Ti' for *Tinker et al., 2010*.
        """

        if self._params.multiplicity_fnct == "PS":
            # Press & Schechter, 'Formation of Galaxies and Clusters of Galaxies by
            # self-similar gravitational condensation' (1974)
            f = np.sqrt(2.0 / np.pi) * np.exp(-(nu**2.0) / 2.0)

        elif self._params.multiplicity_fnct == "ST":
            # Sheth & Tormen, 'Large-scale bias and the peak background split', 1999
            # f = self._params.mf_aa * np.sqrt(2. * self._params.mf_a / np.pi) * \
            #   (1. + (self._params.mf_a * nu ** 2.) ** (-self._params.mf_p)) * np.exp(
            #   - self._params.mf_a * nu ** 2. / 2.)

            f = 0.2161599864561661 * (
                (1.0 + (self._params.mf_a * nu**2.0) ** (-self._params.mf_p))
                * np.exp(-self._params.mf_a * nu**2.0 / 2.0)
            )

        elif self._params.multiplicity_fnct == "Ti":
            # Tinker et al., 'Large-scale bias of dark matter halos', 2010
            f = (
                self._params.mf_aa
                * (1.0 + (self._params.mf_b * nu) ** (-2.0 * self._params.mf_a))
                * nu ** (2.0 * self._params.mf_n)
                * np.exp(-self._params.mf_c * nu**2.0 / 2)
            )
        else:
            raise NotImplementedError(
                "{} for multiplicity_fit in calc_f is not supported, use one of "
                "the following options: 'PS' for Press & Schechter, 'ST' for "
                "Sheth & Tormen, "
                "or 'Ti' for Tinker et al.".format(self._params.multiplicity_fnct)
            )
        return f

    def cm(self, m_msun, a):
        r"""
        *Concentration-mass* function of Dark Matter Haloes. The implemented fitting
        function is from `Bullock et al, 2001
        <https://arxiv.org/abs/astro-ph/9908159>`_,
        as described in Eq. (14) of `Mead et al, 2015
        <https://arxiv.org/abs/1505.07833>`_.

        :param a: scale factor a [1]
        :param m_msun: halo mass in solar masses [Msun]
        :return: Concentration :math:`c(a, M)` of a halo of mass :math:`m_{msun}`
                 at scale factor :math:`a`.
        """
        a = np.atleast_1d(a)
        z = 1.0 / a - 1

        if self._params.w0 != -1:
            raise NotImplementedError(
                "{} for concentration-mass relation is not supported for w!=-1"
            )

        # Bullock et al., 'Profiles of dark haloes: evolution, scatter and environment',
        # 2001 The correction by Dolag is not required

        # Determine the linear growth factor at the formation scale factor as in Eq.
        # (15) of Mead et al, 2015 It is used to calculate the formation scale factor
        # below
        gzf = (
            self.delta_c(a)
            / self.sigma(0.01 * m_msun, a)
            * self._tables.growth_tab_a(a=a)
        )

        # Determine the formation redshift
        af = self._tables.inv_growth_tab_a(g=gzf)
        zf = 1.0 / af - 1.0

        c = self._params.A_mead * (1.0 + zf) / (1.0 + z)
        # If the formation redshift is smaller than z i.e. in the future we set c = A
        c[zf < z] = self._params.A_mead

        return c

    def pk_1h(self, k, a, nu_range):
        r"""
        One-Halo term of the non-linear matter power spectrum as defined in Eq.(8) of
        `Mead et al, 2015 <https://arxiv.org/abs/1505.07833>`_.

        :param k: wavelength :math:`[Mpc^{-1}]`

        :param a: scale factor [1]

        :param nu_range: nu_range-array used for the integration (default set to full
                         lookup table)

        :param mode: integration scheme. The values **0**, **1** and **2** refer to
                     *numpy integration*, *cython integration* and *cython with adaptive
                     integration*, respectively.

        :return: One-Halo power spectrum :math:`P_{1h}(k) \ [Mpc^{3}]`.
        """

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        nu_range = np.atleast_1d(nu_range)

        m_msun = self.nu2mass(nu_range, a)
        # mask = ~np.isnan(m_msun)
        # m_msun = m_msun[mask]

        # Alter the top hat window function as in Eq. (26) of Mead et al., 2015:
        # W(k, M) = W(nu^eta, k, M)
        rv_mpc = self.rvir(m_msun, a)

        c = self.cm(m_msun, a).T
        f = self.f(nu=nu_range)

        eta = self._eta(a)
        integral_1halo = cython_integral_halo(
            k, m_msun, nu_range, rv_mpc, c, a, f, eta, adaptive=1
        )

        pk_1h = integral_1halo / self._params.rho_matter_Msun_iMpc3

        # # Apply the large scale smoothing described in Eq. (24) of Mead et al, 2015
        k_star = 0.584 * self.sigma_v_a(a) ** -1
        pk_1h *= 1.0 - np.exp(-((k[:, None] / k_star) ** 2))
        return pk_1h

    def pk_2h(self, k, a):
        r"""
        Two-Halo term of the non-linear matter power spectrum as defined in Eq.(10) of
        `Mead et al, 2015 <https://arxiv.org/abs/1505.07833>`_.

        :param k: wavelength :math:`[Mpc^{-1}]`
        :param a: scale factor [1]
        :return: Two-Halo power spectrum :math:`P_{2h}(k) \ [Mpc^{3}]`.
        """

        sigma_d_100 = self.sigma_d(a)
        f = 0.0095 * (sigma_d_100 * self._params.h) ** 1.37
        a = np.atleast_1d(a)

        pk_2h = self._tables.powerspec_tab_a_k(k=k, a=a)

        # Apply the damping at quasi-linear scales as described in Eq. (23) of Mead et
        # al., 2015
        pk_2h *= 1.0 - f * np.tanh(k[:, None] * self.sigma_v_a(a) / np.sqrt(f)) ** 2

        return pk_2h

    def print_params(self):
        """
        Prints the cosmological setup and the parameters used for the computation of the
        non-linear matter power spectrum with the Mead et al., 2015 model.

        Example:

        .. code-block:: python

            cosmo.set(pk_nonlin_type = 'mead')
            cosmo.nonlin_pert.print_params()
        """

        COSMO_PARAMS = [
            "h",
            "omega_m",
            "omega_b",
            "omega_l",
            "w0",
            "wa",
            "n",
            "pk_norm",
        ]

        print(
            "The halomodel with Mead et al. corrections has been initialised with the"
            " following attributes:"
        )
        for key in self._params.keys():
            print("{} = {}".format(key, self._params[key]))

        print(
            "The halomodel with Mead et al. corrections has been initialised with the"
            " following cosmological parameters:"
        )
        for key in COSMO_PARAMS:
            print("{} = {}".format(key, self._params[key]))

    def max_redshift(self, k):
        """computes max redshift for which this model is applicable.

        :param k: wavenumber k, might be needed for some underlying linear perturbation
                  models.  [:math:`h Mpc^{-1}`]
        :returns: redshift
        """
        return self._lin_pert.max_redshift(k)

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        r"""
        Calculates the non-linear matter power spectrum, using the ``mead`` model, as
        described in \
        `Mead et al., 2015 <https://arxiv.org/abs/1505.07833>`_ and \
        `Mead et al., 2016 <https://arxiv.org/abs/1602.02154>`_,
        consisting of the superposition
        of the :meth:`pk_1h` and :meth:`pk_2h` terms.


        :param k: wavelength :math:`[Mpc]^{-1}`
        :param a: scale factor [1]
        :param nu_range: nu-array used for the integration [1]
        :param m_min_msun: minimum halo mass for the integration range [Msun]
        :param m_max_msun: maximum halo mass for the integration range [Msun]
        :return: Halo Model power spectrum, :math:`P_{nl}(k)`, in :math:`[Mpc^{3}]`.

        Example:

        .. code-block:: python

            cosmo.set(pk_nonlin_type = 'mead')
            cosmo.nonlin_pert.powerspec_a_k(a,k)
        """

        a = np.atleast_1d(a).astype(float)
        k = np.atleast_1d(k).astype(float)

        a_limit = 1 / (1 + self.max_redshift(k))

        mask_invalid = (a <= a_limit) | (a > 1.0)

        a[mask_invalid] = a_limit

        if diag_only:
            assert len(a) == len(k)

        min_growth = self._tables.growth_tab_a(min(a))
        max_delta_c = self.delta_c(max(a))
        nu_max = (
            max(self.nu0) / self.delta_c_a0 * max_delta_c * self.growth_a0 / min_growth
        )
        nu_range = np.append(
            [1e-100], 10 ** np.linspace(-10, np.log10(nu_max - 0.001), 1000)
        )

        pk_1h = self.pk_1h(k, a, nu_range)
        pk_2h = self.pk_2h(k, a)

        # Adapt the transition between 1-halo and 2-halo term as described in Eq. (27)
        # of Mead et al, 2015
        alpha = self._alpha(a)
        pk = (pk_1h**alpha + pk_2h**alpha) ** (1.0 / alpha)
        pk[:, mask_invalid] = np.nan
        if diag_only:
            return np.diag(pk)
        else:
            return pk
