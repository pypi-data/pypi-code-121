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

import abc
import warnings
import numpy as np
from scipy.interpolate import interp1d


class LinearPerturbationBase(object):
    r"""
    This is the parent class of LinearPerturbationApprox and
    LinearPerturbationBoltzmann.
    It provides some abstract methods for growth factors, transfer functions and the
    linear power spectrum.
    It also calculates :math:`\sigma_8` and :math:`\sigma_r`.
    """

    __metaclass__ = abc.ABCMeta

    def __new__(clz, *a, **kw):
        # check_protypes(clz)
        return super(LinearPerturbationBase, clz).__new__(clz)

    # todo: sigma_r needs to be speeded up and made robust
    # todo: merge this with sigma8
    def sigma_r(self, r=8.0, a=1.0):
        """
        Calculates the rms of the density field on a given scale :math:`r`.
        It is a generalization of the function :meth:`sigma8`.

        :param r: scale radius (default set to :math:`8 h^{-1} Mpc`)
        :return: :math:`\\sigma_r` [1]
        """

        r = np.atleast_1d(r)
        # TODO: numpy based vecoriztion !
        res = np.zeros(shape=r.shape)
        for i in range(0, len(r)):
            ri = r[i]
            k = self._sigma_k_grid()  # grid of wavenumber k [Mpc^-1]
            lnk = np.log(k)
            w = (
                3.0 / (k * ri) ** 2 * (np.sin(k * ri) / (k * ri) - np.cos(k * ri))
            )  # top hat window function
            pk = self.powerspec_a_k(a=1.0, k=k)
            res[i] = np.trapz(k**3 * pk[0] * w**2, lnk)

        return np.sqrt(1.0 / (2.0 * np.pi**2) * res)

    def _sigma_k_grid(self):
        return np.logspace(-5.0, 2.0, num=5000)  # grid of wavenumber k [Mpc^-1]

    def sigma8(self, a=1.0):
        """
        Computes sigma8, the rms density contrast fluctuation smoothed
        with a top hat of radius 8 :math:`h^{-1} Mpc`. This routine is also
        used for the normalization of the power spectrum, when pk_type=``sigma8`` is
        chosen.

        :param a: scale factor [1]
        :return: sigma8 [1]
        """

        is_number = False
        if not isinstance(a, np.ndarray):
            is_number = True
            a = np.atleast_1d(a)
            a = a.astype("float")

        r = 8.0 / self._params.h  # smoothing radius [Mpc]
        k_fine = np.logspace(-5.0, 2.0, num=50000)  # grid of wavenumber k [Mpc^-1]
        k = self._sigma_k_grid()
        lnk = np.log(k)
        res = np.zeros((len(a),))

        for i, ai in enumerate(a):
            pk = self.powerspec_a_k(a=ai, k=k)[:, 0]
            pk_interpolated = interp1d(lnk, pk, "quadratic")

            def integrand(k):
                w = (
                    3.0 / (k * r) ** 2 * (np.sin(k * r) / (k * r) - np.cos(k * r))
                )  # top hat window function
                # fix round off issues of sin(k * r) / (k * r) for small k * r using
                # taylor:
                kr_limit = 1e-2
                kr = r * k[k * r <= kr_limit]
                w[k * r <= kr_limit] = 1 - kr**2 / 10 + kr**4 / 280
                return k**3 * w**2 * pk_interpolated(np.log(k))

            with warnings.catch_warnings():
                integral = np.trapz(integrand(k_fine), np.log(k_fine))
            res[i] = integral

        result = np.sqrt(1.0 / (2.0 * np.pi**2) * res)
        if is_number:
            return result[0]
        return result

    @abc.abstractmethod
    def growth_a(self, a=1.0, k=None, norm=0, diag_only=True):
        ...

    @abc.abstractmethod
    def transfer_k(self, k):
        ...

    @abc.abstractmethod
    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        ...

    @abc.abstractmethod
    def max_redshift(self, k):
        pass
