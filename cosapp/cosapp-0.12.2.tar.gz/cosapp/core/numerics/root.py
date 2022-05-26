"""
Module provides dispatch to different non-linear algorithms.
"""
from __future__ import annotations
import abc
import logging
import inspect
from numbers import Number
from typing import (
    Callable, Optional, Union,
    Sequence, Tuple, Dict, Any,
    TypeVar, Type,
)

import numpy
from scipy.linalg import lu_factor, lu_solve, LinAlgWarning
from scipy import optimize

from cosapp.core.numerics.enum import NonLinearMethods
from cosapp.core.numerics.basics import SolverResults
from cosapp.utils.logging import LogLevel

logger = logging.getLogger(__name__)


ConcreteSolver = TypeVar("ConcreteSolver", bound="BaseNumericSolver")
RootFunction = Callable[[Sequence[float], Any], numpy.ndarray]


class BaseNumericalSolver(abc.ABC):

    def __init__(self, options={}) -> None:
        self.__options = dict(options)

    @property
    def options(self) -> Dict[str, Any]:
        return self.__options

    @classmethod
    def from_options(cls: Type[ConcreteSolver], options: Dict[str, Any]) -> ConcreteSolver:
        solver = cls()
        solver.transfer_options(options)
        return solver

    def transfer_options(self, options: Dict[str, Any]) -> None:
        settings = self.options
        for key in settings.keys():
            try:
                settings[key] = options.pop(key)
            except KeyError:
                continue

    @abc.abstractmethod
    def solve(
        self,
        fun: RootFunction,
        x0: Sequence[float],
        args: Tuple[Any] = tuple(),
        *other_args, **kwargs,
    ) -> Union[SolverResults, optimize.OptimizeResult]:
        pass


class NumpySolver(BaseNumericalSolver):
    """Encapsulation of `scipy.optimize.root`
    """
    def __init__(self, method: str, options={}) -> None:
        """
        Parameters
        ----------
        method: str
            Method forwarded to `scipy.optimize.root`
        options: Dict[str, Any], optional
            A dictionary of solver options. E.g. `tol` or `max_iter`
        """
        self._method = method
        super().__init__(options)
        try:
            self.options.pop('verbose')
        except KeyError:
            pass

    def solve(self,
        fun: RootFunction,
        x0: Sequence[float],
        args: Tuple[Union[float, str]] = (),
        jac=None,
        callback=None,
    ) -> optimize.OptimizeResult:
        """Cancel residues produced by `fun` starting with `x0` as initial guess.

        Parameters
        ----------
        fun : Callable[[Sequence[float], Any], numpy.ndarray[float]]
            Callable residues function
        x0 : Sequence[float]
            Initial solution guess
        args : Tuple[Any, ...]
            Additional arguments passed to `fun`
        jac : bool or callable, optional
            If `jac` is a Boolean and is `True`, `fun` is assumed to return
            the value of Jacobian along with the objective function.
            If `False`, the Jacobian will be estimated numerically.
            `jac` can also be a callable returning the Jacobian of `fun`.
            In this case, it must accept the same arguments as `fun`.
            (default: `None`)
        callback : Callable, optional
            Optional callback function. It is called on every iteration as `callback(x, r)`,
            where x is the current solution and r the corresponding residual.

        Returns
        -------
        scipy.optimize.OptimizeResult
            The solution represented as a OptimizeResult object. Important attributes are: x the solution array,
            success a Boolean flag indicating if the algorithm exited successfully and message which describes the
            cause of the termination. See :py:class:`cosapp.core.numerics.basics.SolverResults` for a description
            of other attributes.
        """
        x0 = numpy.atleast_1d(x0)

        results = optimize.root(
            fun, x0, args=args,
            method=self._method,
            jac=jac,
            tol=self.options.get('tol', None),
            callback=callback,
            options=self.options,
        )
        results.jac_lup = (None, None)
        if 'jac' in results:
            try:
                results.jac_lup = lu_factor(results.jac, check_finite=False)
            except (ValueError, LinAlgWarning) as err:  # Silent LU decomposition failure
                logger.debug(f"Silent error: {err}")

        return results


def get_kwargs():
    """Returns kwargs as a dictionary, using `inspect.currentframe`
    """
    frame = inspect.currentframe().f_back
    keys, _, _, values = inspect.getargvalues(frame)
    kwargs = {}
    for key in keys:
        if key != 'self':
            kwargs[key] = values[key]
    return kwargs


class CustomSolver(BaseNumericalSolver):
    """Custom Newton-Raphson solver.
    """
    def __init__(
        self,
        tol='auto',
        factor=1.0,
        max_iter=100,
        verbose=False,
        eps=2**(-23),
        jac_update_tol=0.01,
        history=False,
        partial_jac=True,
        partial_jac_tries=5,
        tol_update_period=4,
        tol_to_noise_ratio=16,
    ):
        options = get_kwargs()
        super().__init__(options)

    def solve(
        self,
        fresidues: RootFunction,
        x0: Sequence[float],
        args: Tuple[Union[float, str]] = (),
        jac=None,
        recorder=None,
        **options,
    ) -> SolverResults:
        """Customized Newton-Raphson algorithm to solve `fresidues` starting with `x0`.

        Parameters
        ----------
        fresidues : Callable[[Sequence[float], Any], numpy.ndarray[float]]
            Callable residues function
        x0 : Sequence[float]
            Initial solution guess
        args : Tuple[Any, ...]
            Additional arguments for `fun`
        options : dict, optional
            A dictionary of problem-dependent solver options.

        Options
        -------
        jac_lup : (ndarray[float], ndarray[int]), optional
            LU decomposition of Jacobian given as tuple (LU, perm) to reuse as initial direction
        jac : ndarray, optional
            Jacobian to reuse for partial update
        compute_jacobian : bool
            Force to update the Jacobian matrix even if the provided one is useful
        lower_bound : numpy.ndarray
            Min values for parameters iterated by solver.
        upper_bound : numpy.ndarray
            Max values for parameters iterated by solver.
        abs_step : numpy.ndarray
            Max absolute step for parameters iterated by solver.
        rel_step : numpy.ndarray
            Max relative step for parameters iterated by solver.

        Returns
        -------
        SolverResults
            The solution represented as a `SolverResults` object.
            See :py:class:`cosapp.core.numerics.basics.SolverResults` for details.
        """
        solver_options = self.options
        verbose = solver_options.get('verbose', False)
        log_level = LogLevel.INFO if verbose else LogLevel.DEBUG
        jac_update_tol = solver_options.get('jac_update_tol', 0.01)
        jac_rel_perturbation = solver_options['eps']
        factor_ref = factor = solver_options['factor']
        history = solver_options.get('history', False)

        if jac is not None:
            jac = numpy.asarray(jac)
        jac_lu, piv = options.get('jac_lup', (None, None))
        calc_jac = options.get('compute_jacobian', True) or jac is None or jac.shape[1] != x0.shape[0]

        def calc_jacobian(
            x: numpy.ndarray,
            residues: numpy.ndarray,
            it_jac: int,
            it_p_jac: int,
            jac: numpy.ndarray=None,
            r_indices_to_update=set(),
        ) -> Tuple[numpy.ndarray, int, int]:
            """Estimate function gradient with respect to x"""
            n = x.size
            if jac is None or jac.shape != (n, n):
                new_jac = numpy.zeros((n, n), dtype=float)
                x_indices_to_update = list(range(n))
            else:
                new_jac = jac.copy()
                ncol = new_jac.shape[1]
                x_indices_to_update = set()
                for i in r_indices_to_update:
                    x_indices_to_update.update(j for j in range(ncol) if new_jac[i, j] != 0)

            x_copy = x.copy()

            for j in x_indices_to_update:
                delta = jac_rel_perturbation
                if abs(x_copy[j]) >= abs(jac_rel_perturbation):
                    delta = x_copy[j] * jac_rel_perturbation
                x_copy[j] += delta
                logger.debug(f"Perturb unknown {j}")
                perturbation = fresidues(x_copy, *args)
                new_jac[:, j] = (perturbation - residues) * (1 / delta)
                x_copy[j] = x[j]

            n_partial = len(x_indices_to_update)
            if n_partial == n:
                logger.log(log_level, f'Jacobian matrix: full update')
                it_jac += 1
            elif x_indices_to_update:
                it_p_jac += 1
                logger.log(log_level, 
                    f'Jacobian matrix: {n_partial} over {n} derivative(s) updated')

            return new_jac, it_jac, it_p_jac

        logger.debug("NR - Reference call")
        x = numpy.array(x0, dtype=numpy.float64).flatten()
        r = fresidues(x, *args)
        r_norm = numpy.linalg.norm(r, numpy.inf)
        logger.log(log_level, f"Initial residue: {r_norm}")
        logger.log(LogLevel.FULL_DEBUG, f"Initial relaxation factor {factor}.")
        results = SolverResults()

        def check_numerical_features(name, default_value):
            if name not in options or options[name] is None or numpy.shape(options[name]) != x.shape:
                options[name] = numpy.full_like(x, default_value)

        check_numerical_features('lower_bound', -numpy.inf)
        check_numerical_features('upper_bound', numpy.inf)
        check_numerical_features('abs_step', numpy.inf)
        check_numerical_features('rel_step', numpy.inf)

        it_solver = 0
        if recorder is not None:
            record_state = lambda iter: recorder.record_state(str(iter), 'ok',)
        else:
            record_state = lambda iter: None

        if not calc_jac:
            logger.debug('Reuse of previous Jacobian matrix')

        tol = solver_options['tol']
        if tol is None:
            tol = 'auto'
        elif isinstance(tol, str):
            if tol != 'auto':
                raise ValueError(f"Tolerance must be a float, None, or 'auto'.")
        elif not isinstance(tol, Number):
            raise TypeError(f"Tolerance must be a number, None, or 'auto'; got {tol!r}")
        
        auto_tol = (tol == 'auto')
        if auto_tol:
            tol = 0.0
            iter_period = solver_options['tol_update_period']
            tol_to_noise = solver_options['tol_to_noise_ratio']
            must_update_tol = lambda it: it % iter_period == 0
        elif tol < 0:
            raise ValueError(f"Tolerance must be non-negative (got {tol})")
        else:
            tol_to_noise = None
            must_update_tol = lambda it: False

        results.trace = trace = list()
        if history:
            record = {
                "x": x.copy(),
                "residues": r.copy(),
                "tol": tol,
            }
            trace.append(record)

        max_iter = solver_options['max_iter']
        p_jac = solver_options['partial_jac']
        p_jac_tries = solver_options['partial_jac_tries']
        it_jac, it_p_jac = 0, 0  # number of full and partial evalutions of the Jacobian
        n_broyden_update = 0
        dr = numpy.zeros_like(r)
        dx = numpy.full_like(r, numpy.nan)

        rtol_x = 1e-14
        epsilon = numpy.finfo(numpy.float64).eps
        logger.log(
            LogLevel.FULL_DEBUG,
            "\t".join([
                f"iter #{it_solver}",
                f"tol = {tol:.2e}",
                f"|R| = {r_norm}",
                f"x = {x}",
            ])
        )

        try:
            res_index_to_update = set()
            consecutive_p_jac = 0
            prev_tol = -1.0

            while r_norm > tol and it_solver < max_iter:
                logger.log(log_level, f'Iteration {it_solver}')

                if calc_jac:
                    if consecutive_p_jac > p_jac_tries or not p_jac:
                        res_index_to_update = range(x.size)
                        consecutive_p_jac = 0
                    else:
                        consecutive_p_jac += 1

                    jac, it_jac, it_p_jac = calc_jacobian(
                        x, r, it_jac, it_p_jac,
                        jac, res_index_to_update,
                    )
                    jac_lu, piv = self.lu_factor(jac)  # may raise an exception

                elif it_solver > 0:
                    # Good Broyden update - source: https://nickcdryan.com/2017/09/16/broydens-method-in-python/
                    logger.log(log_level, f'Broyden update')
                    n_broyden_update += 1
                    corr = numpy.outer((dr - jac.dot(dx)), dx) / dx.dot(dx)
                    jac += corr
                    jac_lu, piv = self.lu_factor(jac)

                if must_update_tol(it_solver):
                    norm_J = numpy.linalg.norm(jac, numpy.inf)
                    norm_x = numpy.linalg.norm(x, numpy.inf)
                    noise = epsilon * norm_J * norm_x
                    tol = tol_to_noise * noise
                    logger.log(
                        LogLevel.FULL_DEBUG,
                        f"iter #{it_solver}; noise level = {noise}; tol = {tol}; |J| = {norm_J}; |x| = {norm_x}"
                    )
                    if tol == prev_tol:
                        logger.log(log_level, f"Numerical saturation detected at iteration {it_solver}; x = {x}")
                        break
                    prev_tol = tol

                dx = -lu_solve((jac_lu, piv), r)
                it_solver += 1

                # Compute relaxation factors from max absolute and relative steps
                with numpy.errstate(invalid='ignore', divide='ignore'):
                    abs_x = numpy.abs(x)
                    abs_dx = numpy.abs(dx)
                    dx_max_abs = options['abs_step']
                    dx_max_rel = numpy.where(abs_x > 0, abs_x * options['rel_step'], numpy.inf)
                    factor_abs = numpy.where(abs_dx > dx_max_abs, dx_max_abs / abs_dx, 1).min()
                    factor_rel = numpy.where(abs_dx > dx_max_rel, dx_max_rel / abs_dx, 1).min()

                factor = min(factor_rel, factor_abs, factor, 1)

                if factor < factor_ref:
                    logger.debug(f"\trelaxation factor lowered to {factor}")

                r_norm_prev = r_norm
                x_prev = x.copy()
                dx *= factor
                x += dx

                # Force solution within admissible bounds
                # Note:
                #   This is clearly wrong, and does NOT belong in a nonlinear solver.
                #   The correct way to deal with such constraints is to use an optimizer.
                #   This part was only kept for non-regression purposes, but should be
                #   removed in a future revision.
                x = numpy.maximum(x, options['lower_bound'])
                x = numpy.minimum(x, options['upper_bound'])

                new_r = fresidues(x, *args)
                r_norm = numpy.linalg.norm(new_r, numpy.inf)
                # logger.log(log_level, f'Residue: {r_norm:.5g}')
                logger.log(
                    LogLevel.DEBUG,
                    "\t".join([
                        f"iter #{it_solver}",
                        f"tol = {tol:.2e}",
                        f"|R| = {r_norm}",
                        f"x = {x}",
                    ])
                )

                if numpy.allclose(x, x_prev, rtol=rtol_x, atol=0):
                    logger.log(log_level, f"Fixed point detected: x = {x}, dx = {x - x_prev}")
                    break

                # Estimate non-linearity by comparing extrapolated and actual residues
                abs_r = numpy.abs(r)
                extrapolated_r = r + jac.dot(dx)
                delta_vs_linear = numpy.abs(extrapolated_r - new_r)
                res_index_to_update = set(
                    numpy.argwhere(delta_vs_linear > jac_update_tol * abs_r).ravel()
                )
                res_index_to_update -= set(numpy.argwhere(abs_r < tol).ravel())

                r, dr = new_r, new_r - r

                if history:
                    record = {
                        "x": x.copy(),
                        "residues": r.copy(),
                        "tol": tol,
                    }
                    if calc_jac:
                        record["jac"] = jac.copy()
                    trace.append(record)
                
                record_state(it_solver)

                if res_index_to_update:
                    factor = factor_ref
                    calc_jac = True
                elif r_norm != 0:
                    growth_rate = 1 + 0.1 * (1 - factor) * r_norm_prev / r_norm
                    factor = min(growth_rate * factor, 1)
                    calc_jac = False
                    logger.log(LogLevel.FULL_DEBUG, f"New relaxation factor {factor}.")

        except (ValueError, LinAlgWarning):
            is_nil = (jac == 0)
            zero_rows = numpy.argwhere(is_nil.all(axis=1)).flatten()
            zero_cols = numpy.argwhere(is_nil.all(axis=0)).flatten()
            results.success = False
            results.message = 'Singular {}x{} Jacobian matrix'.format(*jac.shape)
            results.jac_errors = {'unknowns': zero_cols, 'residues': zero_rows}
        
        else:
            results.x = x
            results.jac_lup = (jac_lu, piv)
            results.jac_calls = it_jac + it_p_jac
            results.fres_calls = it_solver
            results.success = (r_norm <= tol)
            
            status = f'Converged' if results.success else 'Not converged'
            message = (
                f"{status} ({r_norm:.4e}) in {it_solver} iterations,"
                f" {it_jac} complete, {it_p_jac} partial Jacobian and"
                f" {n_broyden_update} Broyden evaluation(s)"
                f" (tol = {tol:.1e})"
            )
            results.message = f"   -> {message}"

        finally:
            results.jac = jac
            results.tol = tol
            return results

    @staticmethod
    def lu_factor(matrix: numpy.ndarray):
        lu, piv = lu_factor(matrix, check_finite=True)
        min_diag = numpy.abs(lu.diagonal()).min()
        if min_diag < 1e-14:
            raise LinAlgWarning(
                f"Quasi-singular Jacobian matrix; min diag element of U matrix is {min_diag}"
            )
        return lu, piv


def root(
    fun: RootFunction,
    x0: Sequence[float],
    args: Tuple[Any] = tuple(),
    method: NonLinearMethods = NonLinearMethods.POWELL,
    options: Dict[str, Any] = {},
) -> Union[SolverResults, optimize.OptimizeResult]:

    if method == NonLinearMethods.NR:
        solver = CustomSolver.from_options(options)
        return solver.solve(fun, x0, args, **options)
    
    else:
        solver = NumpySolver(method.value, options)
        return solver.solve(fun, x0, args)
