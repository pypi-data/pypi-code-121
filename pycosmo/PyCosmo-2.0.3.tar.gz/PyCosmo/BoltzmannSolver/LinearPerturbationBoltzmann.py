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

import itertools
import multiprocessing
import warnings

from functools import lru_cache

import numpy as np

from ..LinearPerturbationBase import LinearPerturbationBase
from .Fields import Fields
from .LsodaSolver import LsodaSolver


# use decorator to print messages only once per model:
@lru_cache(maxsize=1)
def print_new_traces(cache_file):
    print()
    print("new traces detected! you might want to run")
    print("recompile {}".format(cache_file))
    print()


class LinearPerturbationBoltzmann(LinearPerturbationBase):
    """
    Class for computing linear perturbations by solving the Einstein-Boltzmann ODE
    system.

     The Boltzmann solver is selected using the *set function*:

        .. code-block:: python

            cosmo.set(pk_type = "boltz")

    """

    def __init__(self, cosmology):
        self._cosmo = cosmology
        self._params = cosmology.params
        self._background = cosmology.background
        self._solver = LsodaSolver(
            True,
            self._params.boltzmann_rtol,
            self._params.boltzmann_atol,
            self._params.boltzmann_max_bdf_order,
            self._params.boltzmann_max_iter,
            self._cosmo,
            self._params.fast_solver,
        )
        self._wrapper = self._background._wrapper
        self._background = cosmology.background
        self._fields = Fields(cosmology)
        self._enrich_params()

    def _enrich_params(self):
        if self._params.pk_norm_type == "A_s":
            self._params.As_norm = self._params.pk_norm
        else:
            self._params.As_norm = None

    def _setup_norm(self):
        if self._params.As_norm is None and self._params.pk_norm_type == "sigma8":
            self._params.sigma8 = self._params.pk_norm
            self._params.As_norm = 2.0e-9  # arbitrary temporary value
            sigma8_temp = self.sigma8()
            self._params.As_norm = (
                self._params.As_norm * (self._params.sigma8 / sigma8_temp) ** 2
            )

    def max_redshift(self, k):
        """computes max redshift for which this model is applicable.
        uses the implemented initial conditions to determine this.

        :param k: wavenumber k [:math:`h Mpc^{-1}`]
        :returns: redshift
        """
        k = np.atleast_1d(k)
        a_0 = max(self._solver.initial_conditions(ki)[0] for ki in k)
        return 1 / a_0 - 1

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False, pool=None):
        """
        Returns the linear total matter power spectrum computed from the Boltzmann
        solver, this includes cold dark matter, baryons and massive neutrinos for an
        array of a and k values.

        :param a: scale factor [1] (default:a=1)
        :param k: wavenumber used to compute the power spectrum
                  (default:k=1 Mpc^1) [Mpc^-1]
        :param diag_only: if set to True: compute powerspectrum for pairs
                          :math:`a_i, k_i`, else consider all combinations
                          :math:`a_i, k_j`
        :param pool: instance of multiprocessing.pool.Pool for parallel computation

        .. Warning ::
            If pk_norm_type = 'A_s' this will compute the total matter power spectrum
            following the general relativistic treatment (using delta_m_tot). If
            pk_norm_type = 'deltah' the Poisson equation will be assumed and the
            evolution will be split in growth factor and transfer function. We recommend
            the use of A_s or sigma8 normalizations.

        :return: P(a,k): total matter power spectrum [:math:`Mpc^3`]
        """
        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        if diag_only:
            assert len(a) == len(k)

        if self._params.pk_norm_type == "deltah":
            warnings.warn(
                (
                    "We discourage the use of deltah normalization with the Boltzmann"
                    " solver!"
                ),
                UserWarning,
            )
            T_k = self.transfer_k(k=k, pool=pool)
            growth = self.growth_a(a, k=1)

            # using equation in section 2.4 of notes
            norm = (
                2.0
                * np.pi**2
                * self._params.pk_norm**2
                * (self._params.c / self._params.H0) ** (3.0 + self._params.n)
            )

            if diag_only:
                pk = norm * growth**2 * k**self._params.n * T_k**2
            else:
                pk = norm * np.outer(growth.T**2, k**self._params.n * T_k**2).T
                pk = (
                    norm * growth**2 * (k**self._params.n * T_k**2).reshape(-1, 1)
                )

        if (self._params.pk_norm_type == "A_s") or (
            self._params.pk_norm_type == "sigma8"
        ):

            self._setup_norm()  # renormalization, links sigma8 and A_s

            norm = (
                2.0
                * np.pi**2
                * self._params.As_norm
                / self._params.k_pivot ** (self._params.n - 1)
            )

            src_m = np.zeros((len(a), len(k)))
            kk = k / self._params.h
            for j, onek in enumerate(kk):
                grid, y, meta, keep_lna0 = self._compute_fields(onek, grid=np.log(a))
                delta = y[1:, 1]
                theta = y[1:, 2] * onek 
                delta_b = y[1:, 3]
                theta_b = y[1:, 4] * onek 
                H = self._background.H(a) / (self._params.H0 * self._params.rh)
                omega_nu_m = 0.0
                P_nu_m = 0.0
                omega_m_tot = self._params.omega_m
                omega_plus_p_m_tot = self._params.omega_m
                # include massive neutrinos in the total matter term
                if self._params.N_massive_nu != 0:
                    omega_nu_m = self._wrapper.omega_nu_m_ufunc(a)
                    P_nu_m = self._wrapper.P_nu_m_ufunc(a)
                    omega_m_tot += omega_nu_m / a
                    omega_plus_p_m_tot += (omega_nu_m + P_nu_m) / a
                    delta_nu_m = self._wrapper.delta_nu_m_ufunc(a, y[1:])
                    theta_nu_m = onek * self._wrapper.u_nu_m_ufunc(a, y[1:])
                    src_m[:, j] = (
                        delta_nu_m * omega_nu_m / omega_m_tot / a
                        + (3 * a * H / onek**2)
                        * theta_nu_m
                        * (omega_nu_m + P_nu_m)
                        / a
                        / omega_plus_p_m_tot
                    )

                delta_m_tot = (
                    self._params.omega_dm * delta + self._params.omega_b * delta_b
                )
                theta_m_tot = (
                    self._params.omega_dm * theta + self._params.omega_b * theta_b
                )

                src_m[:, j] += (
                    delta_m_tot / omega_m_tot
                    + (3 * a * H / onek**2) * theta_m_tot / omega_plus_p_m_tot
                )

            pk = norm * src_m.T**2 * k[:, None] ** (self._params.n - 4.0)
            if diag_only:
                return np.diag(pk)

        return pk

    def powerspec_cb_a_k(self, a=1.0, k=0.1, diag_only=False, pool=None):
        """
        Returns the linear matter power spectrum of cold dark matter and baryons
        computed from the Boltzmann solver for an array of a and k values.


        :param a: scale factor [1] (default:a=1)
        :param k: wavenumber used to compute the power spectrum
                  (default:k=1 :math:`Mpc^{-1}`) [:math:`Mpc^{-1}`]
        :param diag_only: if set to True: compute powerspectrum for pairs
                        :math:`a_i, k_i`, else consider all combinations
                        :math:`a_i, k_j`
        :param pool: instance of multiprocessing.pool.Pool for parallel computation

        :return: P_cb(a,k): power spectrum of CDM+baryons [:math:`Mpc^3`]
        """
        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        if diag_only:
            assert len(a) == len(k)

        if self._params.pk_norm_type == "deltah":
            raise ValueError("powerspec_cb_a_k is not supported for deltah normization")

        self._setup_norm()  # renormalization, links sigma8 and A_s

        norm = (
            2.0
            * np.pi**2
            * self._params.pk_norm
            / self._params.k_pivot ** (self._params.n - 1)
        )

        tk = np.zeros((len(a), len(k)))
        kk = k / self._params.h
        for j, onek in enumerate(kk):
            grid, y, meta, keep_lna0 = self._compute_fields(onek, grid=np.log(a))
            delta = y[1:, 1]
            theta = y[1:, 2] * onek
            delta_b = y[1:, 3]
            theta_b = y[1:, 4] * onek
            H = self._background.H(a) / (self._params.H0 * self._params.rh)
            delta_m_tot = self._params.omega_dm * delta + self._params.omega_b * delta_b
            theta_m_tot = self._params.omega_dm * theta + self._params.omega_b * theta_b

            tk[:, j] = (
                delta_m_tot + (3 * a * H / onek**2) * theta_m_tot
            ) / self._params.omega_m

        pk = norm * tk.T**2 * k[:, None] ** (self._params.n - 4.0)

        if diag_only:
            return np.diag(pk)

        return pk

    def growth_a(self, a=1.0, k=None):
        """
        Returns the linear growth factor computed from the Boltzmann solver at a given k
        value.

        :param a: scale factor [1]
        :param k: wavenumber used to compute the growth factor
                  (default:k=1 :math:`Mpc^{-1}`) [:math:`Mpc^{-1}`]

        :return: D(a): growth factor normalised to 1 at a=1 [1]
        """
        assert (
            k is not None
        ), "growth factor of Einstein-Boltzmann model requires a k value"
        # TODO: add option where D is normalised to a in matter dominated era
        grid = np.log(np.atleast_1d(a))
        if grid[-1] != 0.0:
            grid = np.append(grid, [0.0])

        grid, y, meta, keep_lna0 = self._compute_fields(k, grid=grid)
        delta = y[1:, 1]
        growth = delta / delta[-1]

        # if a is a scalar, return a scalar
        if np.isscalar(a):
            return growth[0]
        # if a=1 is contained in a, return all values
        elif a[-1] == 1.0:
            return growth
        # remove the first value, since we added a=1
        else:
            return growth[:-1]

    def _transfer_k(self, args):
        try:
            i, k = args
            kk = np.atleast_1d(k) / self._params.h
            transfer = np.empty_like(kk)
            for index, onek in enumerate(kk):
                grid, y, meta, keep_lna0 = self._compute_fields(
                    onek, [0], keep_lna0=True
                )
                Phi = y[:, 0]
                transfer[index] = Phi[-1] / Phi[0]

            if np.isscalar(k):
                return transfer[0]
            else:
                return transfer
        except Exception:
            import traceback

            traceback.print_exc()
            raise

    def transfer_k(self, k, pool=None):
        """
        Computes the linear matter transfer function using the Boltzmann solver
        assuming the Poisson equation.

        :param k:  wavenumber :math:`[ Mpc^{-1} ]`

        :return: Transfer function :math:`[ Mpc^{3/2} ]`
        """
        a_matter = np.sqrt(self._params.a_eq * self._params.a_eq2)
        corr_fac = self.growth_a(a_matter, k=1.0) / a_matter * 10.0 / 9.0

        if pool is None or np.isscalar(k):
            return self._transfer_k((0, k)) * corr_fac

        assert isinstance(pool, multiprocessing.pool.Pool)

        k = np.array(k)
        n_chunks = min(len(k), len(pool._pool))

        perm = np.argsort(k)
        k = k[perm]
        args = [(i, k[i::n_chunks]) for i in range(n_chunks)]

        results = pool.map(self._transfer_k, args)
        # trick to revert chunking:
        unchunked = np.array(
            [ti for t in itertools.zip_longest(*results) for ti in t if ti is not None]
        )
        inverse_perm = np.arange(len(perm))[perm]
        return corr_fac * unchunked[inverse_perm]

    def fields(
        self,
        k,
        grid,
        sec_factor=5,
        keep_lna0=False,
        initial_conditions=None,
        enable_fast_solver=True,
        enable_sparse_lu_solver=True,
    ):
        """
        Solves the Einstein-Boltzmann ODE system for the evolution
        of the linear order perturbation of the fields.

        :param k: wavenumber :math:`[h/Mpc]`
        :param grid: ln(a) values at which to output fields [1]
        :param sec_factor: relaxes row permutation criterium in optimized LUP solver
        :param keep_lna0: if True includes the fields at initial time a_0
        :param initial_conditions: can pass a_0, y_0 (vector of initial conditions)
        :param enable_fast_solver: if set to False always use standard LUP solver for
                                   full matrix
        :param enable_sparse_lu_solver: if set to True: avoid iterating over known
                                        zero-entries in fallback LUP solver

        :return: Linear order perturbations, accessed with fields.a, fields.Phi etc.
        """
        grid, solver_result, meta, keep_lna_0 = self._compute_fields(
            k,
            grid,
            sec_factor,
            keep_lna0,
            initial_conditions,
            enable_fast_solver,
            enable_sparse_lu_solver,
        )
        self._fields.set_results(grid, solver_result, keep_lna_0)
        self._fields.meta = meta
        return self._fields

    def _sigma_k_grid(self):

        c = self._cosmo
        k_wiggles = np.pi / (c.background.r_s() / c.params.h)
        k_first = 10 ** np.linspace(-5, np.log10(k_wiggles), 10)

        h = np.pi / 5
        n = 22
        k_middle = k_wiggles * np.arange(1, n / h) * h

        k_last = 10 ** np.linspace(np.log10(k_middle[-1]), 2, 10)

        k_grid = np.hstack((k_first, k_middle, k_last))
        # remove duplicates in log values:
        return np.exp(np.array(sorted(set(np.log(k_grid)))))

    def _compute_fields(
        self,
        k,
        grid,
        sec_factor=3,
        keep_lna0=False,
        initial_conditions=None,
        enable_fast_solver=True,
        enable_sparse_lu_solver=True,
    ):

        # self._solver.update_wrapper(self._cosmo.recompile())

        grid = np.atleast_1d(grid)
        grid, solver_result, meta = self._solver.solve(
            k,
            grid,
            sec_factor,
            initial_conditions,
            enable_fast_solver,
            enable_sparse_lu_solver,
        )

        new_traces = meta["new_traces"]
        if (isinstance(new_traces, dict) and new_traces) or (
            isinstance(new_traces, list) and any(new_traces)
        ):
            print_new_traces(self._cosmo._cache_file)
        return grid, solver_result, meta, keep_lna0
