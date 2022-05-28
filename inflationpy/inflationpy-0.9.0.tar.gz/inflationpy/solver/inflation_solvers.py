import itertools
from multiprocessing.sharedctypes import Value
from typing import Dict, List, Optional, Type, Union

import mpmath as mp
import numpy as np
import sympy as sp
import scipy as sc
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.optimize import newton
from scipy.signal import argrelextrema

from IPython.display import display, Math

from inflationpy.core.model import SlowRollModel
from inflationpy.core.functions import InflationFunction


def _display_results(result):
    # Display results:
    i = 0
    for res in result:
        if i == 3:
            display(Math(r"$.....$"))
            break
        elif len(str(res)) <= 500:
            display(res)
            i += 1


def _check_params(functions: List[sp.Expr], remove_symbols: List[sp.Symbol], params):
    params = {str(key): value for key, value in params.items()}
    free_symbols = set()
    for func in functions:
        if isinstance(func, sp.Expr):
            free_symbols = free_symbols.union(func.free_symbols)
    free_symbols = free_symbols - set(remove_symbols)
    excess_parameters = set([str(x) for x in free_symbols]).difference(set(params.keys()))
    if excess_parameters != set():
        raise ValueError(
            f"Some free parameters are not defined. Cannot calculate numerically. ({', '.join(list(excess_parameters))})"
        )
    free_variable_values_dict = {key: params.get(str(key)) for key in list(free_symbols)}
    return free_variable_values_dict


class SlowRollStartSolver:
    def __init__(self, model: Union[InflationFunction, SlowRollModel], invariant=False, display: bool = False) -> None:
        if not isinstance(model, (InflationFunction, SlowRollModel)):
            raise TypeError("Inserted function must be InflationFunction/SlowRollModel type.")
        if isinstance(model, InflationFunction):
            self.function = model
        elif isinstance(model, SlowRollModel):
            if invariant is False:
                if not isinstance(model.A, InflationFunction):
                    raise TypeError(
                        f"A function not defined. A function must be InflationFunction type. {type(model.A)}"
                    )
                if not isinstance(model.B, InflationFunction):
                    raise TypeError(
                        f"B function not defined. B function must be InflationFunction type. {type(model.B)}"
                    )
                if not isinstance(model.V, InflationFunction):
                    raise TypeError(
                        f"V function not defined. V function must be InflationFunction type. {type(model.V)}"
                    )
                self.function = model.N_integrand
            else:
                if not isinstance(model.I_V, InflationFunction):
                    raise TypeError(
                        f"I_V function has not been defined. V function must be InflationFunction type. {type(model.V)}"
                    )
                self.function = model.N_integrandI

        self.display: bool = display

    @staticmethod
    def _get_sym_solution_from_finiteset(solutions):
        result = []
        piecewise_flag = False
        for elem in solutions.args:
            if isinstance(elem, sp.Piecewise):
                piecewise_flag = True
                for elem2 in elem.args:
                    result.append(elem2.args[0])
            else:
                result.append(elem)
        if piecewise_flag:
            print("There are conditions for certain solutions.")

        return result

    @staticmethod
    def _modify_results_with_lambertw(result):
        new_result = []
        for sol in result:
            if sol.has(sp.LambertW):
                lambert_args = [e.args[0] for e in sp.preorder_traversal(sol) if isinstance(e, sp.LambertW)]
                old_lambert = [sp.LambertW(arg) for arg in lambert_args]
                # Add all possible branch variants in (branch 0 and -1 or upper and lower). Other branches will give imaginary values.
                count = len(lambert_args)  # How many lambertW in solution
                branches = set(itertools.permutations(count * [0] + count * [-1], r=count))
                # How many combinations for different branches LambertW. len(branches) == 2^count
                assert len(branches) == 2**count, f"Number of combinations must be 2^count ({2**count})"
                for branch in branches:
                    new_lambert = [sp.LambertW(lambert_args[i], branch[i]) for i in range(count)]
                    # Create substitution list
                    substitutions = list(zip(old_lambert, new_lambert))
                    new_result.append(sol.subs(substitutions))
            else:
                new_result.append(sol)
        return new_result

    def solve(
        self,
        end_value: Union[int, float, mp.mpf, sp.Expr],
        interval=sp.Reals,
        simplify=False,
        method="solve",
        solve_kwargs={"force": True},
    ):
        N = sp.Symbol("N", real=True, positive=True)
        # Integral of V/V' from field_end to field_start
        integral = sp.integrate(self.function.f_s(), (self.function.symbol, end_value, self.function.symbol))
        if isinstance(integral, sp.Integral):
            print("Couldn't solve integral analytically.")
            return []
        elif integral.has(sp.I):
            print("Solution has complex number in.")
        elif integral.has(sp.oo) or integral.has(-sp.oo):
            print("Solution has infinity in.")
            return []

        # Solve N = f(phi) -> phi = f(N)
        equation = sp.Eq(N, integral)

        result = []
        if method == "solveset":
            solutions = sp.solveset(equation, self.function.symbol, domain=interval)
            if isinstance(solutions, sp.Union):
                print("Solution is some union. Specify interval.")
                display(solutions)
            elif isinstance(solutions, sp.sets.sets.EmptySet):
                print("Couldn't find any solutions")
            elif isinstance(solutions, sp.sets.sets.EmptySet):
                print("Solution is expressed as some condition. If possible, define solution(s) manually.")
                display(solutions)
            elif isinstance(solutions, sp.Intersection):
                possible_solutions = solutions.args[-1]
                if isinstance(possible_solutions, sp.FiniteSet):
                    result = self._get_sym_solution_from_finiteset(possible_solutions)
                    print(
                        "Solution is expressed as intersection. Solution might be wrongly interpreted. Might need to define solution(s) manually."
                    )
                else:
                    print("Couldn't interpret solution(s). Please add solution(s) manually.")
                display(solutions)
            elif isinstance(solutions, sp.FiniteSet):
                result = self._get_sym_solution_from_finiteset(solutions)
            else:
                NotImplementedError("Got unexpected type of solutions.")
        elif method == "solve":
            result = list(sp.solve(equation, self.function.symbol, **solve_kwargs))  # type: ignore

        if simplify:
            result = [sp.simplify(x, inverse=True) for x in result]

        # Sort such that solutions which have imaginary in will be last
        result = self._modify_results_with_lambertw(result)
        result.sort(key=lambda x: x.has(sp.I))
        if self.display:
            _display_results(result)

        return result

    def nsolve_mp(
        self,
        end_value: Union[int, float, sp.Expr, mp.mpf],
        N_max: Union[float, int, mp.mpf] = 100,
        solver=None,
        params={},
        mp_kwargs={},
    ):
        if isinstance(end_value, sp.Expr):
            params = _check_params([self.function.f_s(), end_value], [self.function.symbol], params)
            end_value = end_value.subs(params)

        dif_equation = 1 / self.function(params)

        if isinstance(end_value, sp.Expr):
            end_value = mp.convert(sp.N(end_value, mp.mp.dps))
        else:
            end_value = mp.convert(end_value)

        function = lambda x: dif_equation.f_n(x, mode="mpmath")

        if solver is None:
            result_function = self._numeric_solver_mp1(function, end_value, N_max, **mp_kwargs)
        else:
            result_function = solver(function, end_value, N_max)
        return result_function

    def nsolve_np(
        self,
        end_value: Union[int, float, sp.Expr],
        N_max: Union[float, int] = 100,
        solver=None,
        params={},
        sc_kwargs={},
    ):
        if isinstance(end_value, sp.Expr):
            params = _check_params([self.function.f_s(), end_value], [self.function.symbol], params)
            end_value = end_value.subs(params)

        dif_equation = 1 / self.function(params)
        if isinstance(end_value, sp.Expr):
            end_value = float(sp.N(end_value, mp.mp.dps))
        else:
            end_value = float(end_value)

        function = lambda x: dif_equation.f_n(x, mode="scipy")

        if solver is None:
            result_function = self._numeric_solver_np1(function, end_value, N_max, **sc_kwargs)
        else:
            result_function = solver(function, end_value, N_max)
        return result_function

    def _numeric_solver_np1(self, fn, end_value, N_max, **kwargs):
        fun = lambda x, y: fn(y)
        if kwargs.get("method", None) is None:
            kwargs["method"] = "LSODA"
        ode = solve_ivp(fun, t_span=[0, N_max], y0=[float(end_value)], dense_output=True, **kwargs)
        if ode.status == -1:
            raise RuntimeError("Integration step failed. (scipy ode solver)")
        elif ode.status == 1:
            raise RuntimeError("A termination event occurred. (scipy ode solver)")
        # N_function = interp1d(N_points, ode.y.reshape(-1))
        N_function = lambda y: ode.sol(y).reshape(-1)
        return N_function

    def _numeric_solver_mp1(self, fn, end_value, N_max, **kwargs):
        fun = lambda x, y: fn(y)
        N_function = mp.odefun(fun, x0=0, y0=mp.convert(end_value), **kwargs)
        N_function(N_max)
        return N_function


class SlowRollEndSolver:
    def __init__(self, model: Union[InflationFunction, SlowRollModel], invariant=False, display: bool = False) -> None:
        if not isinstance(model, (InflationFunction, SlowRollModel)):
            raise TypeError("Inserted function must be InflationFunction/SlowRollModel type.")
        if isinstance(model, InflationFunction):
            self.function = model
        elif isinstance(model, SlowRollModel):
            if invariant is False:
                if not isinstance(model.A, InflationFunction):
                    raise TypeError(
                        f"A function not defined. A function must be InflationFunction type. {type(model.A)}"
                    )
                if not isinstance(model.B, InflationFunction):
                    raise TypeError(
                        f"B function not defined. B function must be InflationFunction type. {type(model.B)}"
                    )
                if not isinstance(model.V, InflationFunction):
                    raise TypeError(
                        f"V function not defined. V function must be InflationFunction type. {type(model.V)}"
                    )
                self.function = model.epsilon
            else:
                if not isinstance(model.I_V, InflationFunction):
                    raise TypeError(f"I_V function must be InflationFunction type. {type(model.I_V)}")
                self.function = model.epsilonI

        self.display: bool = display

    @staticmethod
    def _modify_results_with_lambertw(result):
        new_result = []
        for sol in result:
            if sol.has(sp.LambertW):
                lambert_args = [e.args[0] for e in sp.preorder_traversal(sol) if isinstance(e, sp.LambertW)]
                old_lambert = [sp.LambertW(arg) for arg in lambert_args]
                # Add all possible branch variants in (branch 0 and -1 or upper and lower). Other branches will give imaginary values.
                count = len(lambert_args)  # How many lambertW in solution
                branches = set(
                    itertools.permutations(count * [0] + count * [-1], r=count)
                )  # How many combinations for different branches LambertW. len(branches) == 2^count
                assert len(branches) == 2**count, f"Number of combinations must be 2^count ({2**count})."
                for branch in branches:
                    new_lambert = [sp.LambertW(lambert_args[i], branch[i]) for i in range(count)]
                    # Create substitution list
                    substitutions = list(zip(old_lambert, new_lambert))
                    new_result.append(sol.subs(substitutions))
            else:
                new_result.append(sol)
        return new_result

    @staticmethod
    def _get_sym_solution_from_finiteset(solutions):
        result = []
        piecewise_flag = False
        for elem in solutions:
            if isinstance(elem, sp.Piecewise):
                piecewise_flag = True
                for elem2 in elem.args:
                    result.append(elem2.args[0])
            else:
                result.append(elem)
        if piecewise_flag:
            print("There are conditions for certain solutions.")

        return result

    def solve(self, interval=sp.Reals, simplify=False, method="solve", solve_kwargs={"force": True}):
        if isinstance(interval, list):
            if len(interval) != 2:
                raise ValueError("List must be length of two. Must include only start and end point")
            elif not all(isinstance(n, (int, float)) for n in interval):
                raise ValueError("Interval list values must be integers of floats.")
            elif interval[0] >= interval[1]:
                raise ValueError("Interval list first element must be smaller then the second one.")
            interval = sp.Interval(interval[0], interval[1])
        elif isinstance(interval, sp.Interval):
            pass
        else:
            raise TypeError("Interval must be list with length 2 (format [x0, x1]) or sympy Interval.")

        analytic_function = self.function.f_s() - 1
        """
            At first try to use solveset, but if this is Emptyset, ImageSet, ConditionSet then ask for interval.
            Results must be concrete values and not expressed as introducing new parameters
            For example: sin(x) = 0 -> x = nπ introduces new parameter n which we don't know beforehand.
        """
        result = []
        if method == "solveset":
            solutions = sp.solveset(analytic_function, self.function.symbol, domain=interval)
            if isinstance(solutions, sp.Union):
                print("Solution is some union. Specify interval.")
                display(solutions)
            elif isinstance(solutions, sp.sets.sets.EmptySet):
                print("Couldn't find any solutions")
            elif isinstance(solutions, sp.sets.sets.EmptySet):
                print("Solution is expressed as some condition. If possible, define solution(s) manually.")
                display(solutions)
            elif isinstance(solutions, sp.Intersection):
                possible_solutions = solutions.args[-1]
                if isinstance(possible_solutions, sp.FiniteSet):
                    result = self._get_sym_solution_from_finiteset(solutions)
                    print(
                        "Solution is expressed as intersection. Solution might be wrongly interpreted. Might need to define solution(s) manually."
                    )
                else:
                    print("Couldn't interpret solution(s). Please add solution(s) manually.")
                display(solutions)
            elif isinstance(solutions, sp.FiniteSet):
                result = self._get_sym_solution_from_finiteset(solutions)
            else:
                NotImplementedError("Got unexpected type of solutions.")
        elif method == "solve":
            result = list(sp.solve(analytic_function, self.function.symbol, **solve_kwargs))  # type: ignore

        if simplify:
            result = [sp.simplify(x, inverse=True) for x in result]

        # Sort such that solutions which have imaginary in will be last
        result.sort(key=lambda x: x.has(sp.I))

        # Display results:
        if self.display:
            _display_results(result)

        return result

    def nsolve_mp(self, interval, solver=None, params={}, mp_kwargs={}):
        if not isinstance(interval, list):
            raise TypeError("Interval must be list type.")
        if len(interval) != 2:
            raise ValueError("Interval list must contain only start and end value.")
        if interval[0] > interval[1]:
            interval = [interval[1], interval[0]]
        params: dict = _check_params([self.function.f_s()], [self.function.symbol], params)
        epsilon: InflationFunction = self.function(params)

        function = lambda x: epsilon.f_n(x, mode="mpmath") - 1
        derivative = lambda x: epsilon.fd_n(x, mode="mpmath")
        derivative2 = lambda x: epsilon.f2d_n(x, mode="mpmath")

        if solver is None:
            if mp_kwargs.get("solver", None) is None:
                mp_kwargs["solver"] = "halley"
            else:
                if not (mp_kwargs["solver"] in ["newton", "mnewton", "halley"]):
                    raise ValueError(
                        f"This solution assmues mp.findroot has solver 'newton', 'mnewton' or 'halley'. ({mp_kwargs['solver']})"
                    )
            if mp_kwargs.get("N_points", None) is None:
                mp_kwargs["N_points"] = 100_000
            if mp_kwargs.get("use_f2d", None) is None:
                mp_kwargs["use_f2d"] = False

            mp_kwargs["np_function"] = lambda x: epsilon.f_n(x, mode="numpy") - 1
            result = self._numeric_solver_mp1(function, interval, derivative, derivative2, **mp_kwargs)
        else:
            result = solver(function, interval, derivative, derivative2)
        result = list(set(result))

        return result

    def nsolve_np(self, interval, solver=None, params={}, sc_kwargs={}):
        if not isinstance(interval, list):
            raise TypeError("Interval must be list type.")
        if len(interval) != 2:
            raise ValueError("Interval list must contain only start and end value.")
        if interval[0] > interval[1]:
            interval = [interval[1], interval[0]]
        params: dict = _check_params([self.function.f_s()], [self.function.symbol], params)
        epsilon: InflationFunction = self.function(params)

        function = lambda x: epsilon.f_n(x) - 1
        derivative = lambda x: epsilon.fd_n(x)
        derivative2 = lambda x: epsilon.f2d_n(x)

        if solver is None:
            solver = self._numeric_solver_np1
            if sc_kwargs.get("maxiter", None) is None:
                sc_kwargs["maxiter"] = 500
            if sc_kwargs.get("disp", None) is None:
                sc_kwargs["disp"] = False
            if sc_kwargs.get("N_points", None) is None:
                sc_kwargs["N_points"] = 10_000
            if sc_kwargs.get("use_f2d", None) is None:
                sc_kwargs["use_f2d"] = False
            result = solver(function, interval, derivative, derivative2, **sc_kwargs)
        else:
            result = solver(function, interval, derivative, derivative2)

        result = np.unique(result)

        return result

    def _possible_solutions(self, fn_np, interval, N_points):
        interval = [float(interval[0]), float(interval[1])]
        with np.errstate(invalid="ignore", divide="ignore"):
            x = np.linspace(interval[0], interval[1], N_points)
            y = np.abs(fn_np(x))
            possible_solutions = np.array(x[argrelextrema(y, np.less)], dtype=float)
            return possible_solutions

    def _numeric_solver_np1(self, fn, interval, fd, f2d, **kwargs):
        """
        Implented method which first looks for local minimas of abs(function). Then for each point it will use scipy function to find more precise root value.
        It does not find always the solutions. Main problem is that if domain space for field values isn't dense enough then it might miss some roots and scipy solver
        won't converge as well.

        Parameters
        ----------
        fn : _type_
            _description_
        interval : _type_
            _description_
        fd : _type_
            _description_
        f2d : _type_
            _description_
        """
        N_points = kwargs.pop("N_points")
        if kwargs.pop("use_f2d"):
            with np.errstate(invalid="ignore", divide="ignore"):
                possible_solutions = np.array(self._possible_solutions(fn, interval, N_points), dtype=float)
                roots = newton(fn, possible_solutions.astype(float), fprime=fd, fprime2=f2d, **kwargs)
                roots = roots[((interval[0] <= roots) & (roots <= interval[1]))]
        else:
            with np.errstate(invalid="ignore", divide="ignore"):
                possible_solutions = np.array(self._possible_solutions(fn, interval, N_points), dtype=float)
                roots = newton(fn, possible_solutions.astype(float), fprime=fd, **kwargs)
                roots = roots[((interval[0] <= roots) & (roots <= interval[1]))]
        return roots

    def _numeric_solver_mp1(self, fn, interval, fd, f2d, **kwargs):
        """
        Implented method which first looks for local minimas of abs(function). Then for each point it will use scipy function to find more precise root value.
        It does not find always the solutions. Main problem is that if domain space for field values isn't dense enough then it might miss some roots and scipy solver
        won't converge as well.

        Parameters
        ----------
        fn : _type_
            _description_
        interval : _type_
            _description_
        fd : _type_
            _description_
        f2d : _type_
            _description_
        """
        roots = []
        N_points = kwargs.pop("N_points")
        possible_solutions = self._possible_solutions(kwargs.get("np_function"), interval, N_points)
        kwargs.pop("np_function", None)
        if kwargs.pop("use_f2d"):
            for pos_sol in possible_solutions:
                root = mp.findroot(f=fn, x0=mp.convert(pos_sol), df=fd, d2f=f2d, **kwargs)
                roots.append(root)
            roots = [x for x in roots if interval[0] <= x <= interval[1]]
        else:
            for pos_sol in possible_solutions:
                root = mp.findroot(f=fn, x0=mp.convert(pos_sol), df=fd, **kwargs)
                roots.append(root)
            roots = [x for x in roots if interval[0] <= x <= interval[1]]
        return roots
