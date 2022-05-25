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

import pickle
from functools import wraps

import numpy as np


class _PowerSpecCache:
    """internal use only: used to avoid repeated computation of the powerspectrum"""

    def __init__(self):
        self.clear()

    def cache(self, power_spec_function):
        @wraps(power_spec_function)
        def wrapped(a, k, diag_only):
            ak = a
            if isinstance(a, np.ndarray):
                ak = a.data.tobytes()
            kk = a
            if isinstance(k, np.ndarray):
                kk = k.data.tobytes()
            key = (power_spec_function.__func__.__qualname__, ak, kk, diag_only)
            if key not in self._cache:
                self._cache[key] = power_spec_function(a, k, diag_only)
            return self._cache[key]

        return wrapped

    def clear(self):
        self._cache = dict()


class Projection(object):
    """
    Core projection functions to be used by the :class:`.Obs` class to predict
    observables.

    .. Warning ::
        Projection not supported by the Boltzmann solver yet, since it requires
        nonlinear perturbations.  Calling any function from this module while using the
        Boltzmann solver (pk_type = 'boltz') will return **ValueError: you must set
        pk_nonlin_type to access projections**
    """

    def __init__(self, params, background, lin_pert, nonlin_pert):

        self.params = params
        self.background = background
        self._memory = _PowerSpecCache()
        self._lin_pert = lin_pert
        self._nonlin_pert = nonlin_pert
        self._setup_cached_powerspec_functions()

    def _setup_cached_powerspec_functions(self):
        self._lin_powerspec_a_k = self._memory.cache(self._lin_pert.powerspec_a_k)
        self._nonlin_powerspec_a_k = self._memory.cache(self._nonlin_pert.powerspec_a_k)

    def __getstate__(self):
        dd = self.__dict__.copy()
        dd.pop("_lin_powerspec_a_k")
        dd.pop("_nonlin_powerspec_a_k")
        return dd

    def __setstate__(self, dd):
        self.__dict__.update(dd)
        self._setup_cached_powerspec_functions()

    def cl_limber(
        self,
        ells,
        weight_function1,
        weight_function2,
        a_grid,
        cosmo,
        perturb="nonlinear",
    ):
        r"""
        Computes the angular power spectrum of the auto- or cross-correlation between
        two LSS probes i.e. galaxy overdensity, cosmic shear or CMB lensing.

        :param ells: array of angular multipoles :math:`\ell`
        :param weight_function1: radial weight function for first probe
        :param weight_function2: radial weight function for second probe
        :param a_grid: integration grid in scale factor a
        :param perturb: string tag denoting if we use linear or nonlinear power
                        spectrum. It can be either ``linear`` or ``nonlinear``.
        :return: Angular power spectrum :math:`C_{\ell}` at the multipoles :math:`\ell`.
        """

        amin, amax, num = a_grid
        amin, amax = min(amin, amax), max(amin, amax)
        a_vec = np.linspace(amin, amax, int(num))  # use a as integration variable
        intg_vec = self.cl_limber_int(
            a_vec, ells, weight_function1, weight_function2, cosmo, perturb
        )
        cl = np.trapz(intg_vec, a_vec, axis=1)

        return cl

    def cl_limber_int(
        self, a, ells, weight_function1, weight_function2, cosmo, perturb="nonlinear"
    ):
        r"""
        Returns the integrand needed to compute the angular power spectrum of the auto-
        or cross-correlation between two LSS probes in the Limber approximation.

        :param a: array of scale factor values a
        :param ells: array of angular multipoles :math:`\ell`
        :param weight_function1: radial weight function for first probe
        :param weight_function2: radial weight function for second probe
        :param perturb: string tag denoting if we use linear or nonlinear power
                        spectrum.  It can be either ``linear`` or ``nonlinear``.

        :return: Integrand at :math:`\ell` for the values of a.
        """

        r = self.background.dist_trans_a(a=a)
        weightfunc = (
            weight_function1(a, self)
            * weight_function2(a, self)
            / r**2
            / a**2
            / self.background.H(a)
            * self.params.c
        )

        avec = np.tile(a, len(ells))
        weightvec = np.tile(weightfunc, len(ells))
        kvec = np.outer(ells, 1 / r).flatten()

        if perturb == "linear":
            intg = weightvec * self._lin_powerspec_a_k(avec, kvec, diag_only=True)
        elif perturb == "nonlinear":
            intg = weightvec * self._nonlin_powerspec_a_k(avec, kvec, diag_only=True)
        else:
            raise ValueError("perturb {} not implemented".format(perturb))

        intg = intg.reshape(len(ells), -1)
        return intg

    def cl_limber_ISW(
        self,
        ell,
        weight_function1,
        weight_function2,
        growth_ISW,
        a_grid,
        perturb="linear",
    ):
        r"""
        Computes the angular power spectrum of the cross correlation between
        the CMB temperature anisotropies and the galaxy overdensity/cosmic shear.

        :param ell: array of angular multipole :math:`\ell`
        :param weight_function1: radial weight function for first probe
        :param weight_function2: radial weight function for second probe
        :param growth_ISW: growth function for ISW
        :param a_grid: integration grid in scale factor a
        :param linear: string tag denoting if we use linear or nonlinear power spectrum.
                       It can be either ``linear`` or ``nonlinear``
        :return: Angular power spectrum :math:`C_{\ell}` at the multipoles :math:`\ell`.
        """

        # There is no minus sign in the integrand, i.e. we don't need to reverse the
        # integration range
        amin, amax, num = a_grid
        amin, amax = min(amin, amax), max(amin, amax)
        # this code requires descending a values to work:
        a_vec = np.linspace(amin, amax, int(num))[::-1]  # use a as integration variable
        intg_vec = self.cl_limber_ISW_int(
            a_vec, ell, weight_function1, weight_function2, growth_ISW, perturb
        )
        # cl = np.trapz(intg_vec,a_vec)
        cls = np.trapz(intg_vec, a_vec, axis=1)

        cls *= (
            3.0
            * self.params.omega_m
            * self.params.H0**2
            * self.params.Tcmb
            / self.params.c**2
            * 1.0
            / ell**2
        )

        return cls

    def cl_limber_ISW_int(
        self, a, ells, weight_function1, weight_function2, growth_ISW, perturb="linear"
    ):
        r"""
        Returns the integrand needed to compute the angular power spectrum of the cross
        correlation between the CMB temperature anisotropies and the galaxy
        overdensity/cosmic shear/CMB lensing.

        :param a: array of scale factor values a
        :param ells: array of angular multipoles :math:`\ell`
        :param weight_function1: radial weight function for first probe
        :param weight_function2: radial weight function for second probe
        :param growth_ISW: growth function for ISW
        :param perturb: string tag denoting if we use linear or nonlinear power
                        spectrum.  It can be either ``linear`` or ``nonlinear``.

        :return: Integrand at :math:`\ell` for the values of a.
        """

        r = self.background.dist_trans_a(a=a)
        weightfunc = (
            weight_function1(a, self) * weight_function2(a, self) * growth_ISW(a, self)
        )
        # TODO This is for a vectorised call - need to remove at some point

        avec = np.ones(len(ells) * len(a))
        weightvec = np.tile(weightfunc, len(ells))
        kvec = np.outer(ells, 1 / r).flatten()

        if perturb == "linear":
            intg = weightvec * self._lin_powerspec_a_k(avec, kvec, diag_only=True)
        else:
            intg = weightvec * self._nonlin_powerspec_a_k(avec, kvec, diag_only=True)

        intg = intg.reshape(len(ells), -1)

        return intg

    def cl_limber_IG(
        self, ell, weight_function1, weight_function2, F, a_grid, IAmodel="NLA"
    ):
        r"""
        Computes the angular power spectrum of the cross correlation between intrinsic
        galaxy ellipticities and tracers of the LSS.

        :param ell: array of angular multipole :math:`\ell`
        :param weight_function1: radial weight function for first probe -> this needs to
                                 be the weight function
        :param weight_function2: radial weight function for second probe -> this needs
                                 to be n(z)
        :param F: IA bias function
        :param a_grid: integration grid in scale factor a
        :param IAmodel: string tag denoting if we use NLA or LA IA model. It can be
                        either ``NLA`` or ``IA``.

        :return: Angular power spectrum :math:`C_{\ell}` at the multipoles :math:`\ell`.
        """

        amin, amax, num = a_grid
        amin, amax = min(amin, amax), max(amin, amax)
        a_vec = np.linspace(amin, amax, int(num))
        intg_vec = self.cl_limber_IG_int(
            a_vec, ell, weight_function1, weight_function2, F, IAmodel
        )
        # cl = np.trapz(intg_vec,a_vec)
        cls = np.trapz(intg_vec, a_vec, axis=1)

        return cls

    def cl_limber_IG_int(
        self, a, ells, weight_function1, weight_function2, F, IAmodel="NLA"
    ):
        r"""
        Returns the integrand for the angular power spectrum of intrinsic alignments
        (IAs) computed using the NLA or LA model.

        :param a: array of scale factor values a
        :param ells: array of angular multipoles :math:`\ell`
        :param weight_function1: radial weight function for first probe -> this needs to
                                 be the weight function
        :param weight_function2: radial weight function for second probe -> this needs
                                 to be n(z)
        :param F: IA bias function
        :param IAmodel: string tag denoting if we use NLA or LA IA model. It can be
                        either ``NLA`` or ``IA``.

        :return: Integrand at :math:`\\ell` for the values of a.
        """

        r = self.background.dist_trans_a(a=a)
        # For the second redshift selection functions, we need to transform a to z
        z = 1.0 / a - 1.0
        weightfunc = (
            weight_function1(a, self)
            * weight_function2(z)
            * F(a, self)
            / r**2
            / a**2
        )

        avec = np.tile(a, len(ells))
        weightvec = np.tile(weightfunc, len(ells))
        kvec = np.outer(ells, 1.0 / r).flatten()

        if IAmodel == "NLA":
            intg = weightvec * self._nonlin_powerspec_a_k(avec, kvec, diag_only=True)
        else:
            intg = weightvec * self._lin_powerspec_a_k(avec, kvec, diag_only=True)

        intg = intg.reshape(len(ells), -1)

        return intg

    def cl_limber_II(
        self, ell, weight_function1, weight_function2, F, a_grid, IAmodel="NLA"
    ):
        r"""
        Computes the angular power spectrum of the auto power spectrum of
        intrinsic galaxy ellipticities.

        :param ell: array of angular multipole :math:`\ell`
        :param weight_function1: redshift selection function for first probe
        :param weight_function2: redshift selection function for second probe
        :param F: IA bias function
        :param a_grid: integration grid in scale factor a
        :param IAmodel: string tag denoting if we use NLA or LA IA model. It can be
                        either ``NLA`` or ``IA``.

        :return: Angular power spectrum :math:`C_{\ell}` at the multipoles :math:`\ell`.
        """

        amin, amax, num = a_grid
        amin, amax = min(amin, amax), max(amin, amax)
        a_vec = np.linspace(amin, amax, int(num))
        intg_vec = self.cl_limber_II_int(
            a_vec, ell, weight_function1, weight_function2, F, IAmodel
        )
        cls = np.trapz(intg_vec, a_vec, axis=1)

        return cls

    def cl_limber_II_int(
        self, a, ells, weight_function1, weight_function2, F, IAmodel="NLA"
    ):
        r"""
        Returns the integrand for the angular power spectrum of the auto correlation of
        intrinsic alignments (IAs) computed using the NLA or LA model.

        :param a: array of scale factor values a
        :param ells: array of angular multipoles :math:`\ell`
        :param weight_function1: redshift selection function for first probe
        :param weight_function2: redshift selection function for second probe
        :param F: IA bias function
        :param IAmodel: string tag denoting if we use NLA or LA IA model. It can be
                        either ``NLA`` or ``IA``.
        :return: Integrand at :math:`\ell` for the values of a.
        """

        r = self.background.dist_trans_a(a=a)
        # For the redshift selection functions, we need to transform a to z
        z = 1.0 / a - 1.0
        weightfunc = (
            self.background.H(a=a)
            / self.params.c
            * weight_function1(z)
            * weight_function2(z)
            * F(a, self) ** 2
            / r**2
            / a**2
        )

        avec = np.tile(a, len(ells))
        weightvec = np.tile(weightfunc, len(ells))
        kvec = np.outer(ells, 1.0 / r).flatten()

        if IAmodel == "NLA":
            intg = weightvec * self._nonlin_pert.powerspec_a_k(
                avec, kvec, diag_only=True
            )
        else:
            intg = weightvec * self._lin_pert.powerspec_a_k(avec, kvec, diag_only=True)

        return intg.reshape(len(ells), -1)
