from abc import ABC, abstractmethod
from typing import Optional, Type, Union, List, Callable, Iterable

import sympy as sp
import numpy as np
import scipy as sc
import mpmath as mp
from scipy.interpolate import interp1d
from scipy.integrate import solve_ivp

from IPython.display import display, Math


from inflationpy.core.functions import InflationFunction
from inflationpy.core.model import SlowRollModel


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


class FunctionSolver(ABC):
    def __init__(
        self,
        model: Optional[SlowRollModel] = None,
    ) -> None:
        super().__init__()
        if not isinstance(model, SlowRollModel):
            raise TypeError("Inserted function must be SlowRollModel type.")
        else:
            self.A = model.A
            self.B = model.B
            self.V = model.V
            self.F = model.F
            self.I_V = model.I_V
            self.symbol = model.symbol
            self.symbolI = model.symbolI
            self.mp = model.mp
            self.palatini = model.palatini

        self.IV_symbol = sp.Symbol("I_V", real=True)
        self.A_symbol = sp.Symbol("A", real=True, positive=True)
        self.B_symbol = sp.Symbol("B", real=True)
        self.V_symbol = sp.Symbol("V", real=True)

    @abstractmethod
    def solve(self):
        """
        Solve problem analytically.
        """
        pass

    @abstractmethod
    def nsolve_np(self):
        """
        Solve problem numerically with numpy/scipy.
        """
        pass

    @abstractmethod
    def nsolve_mp(self):
        """
        Solve problem numerically with mpmath.
        """
        pass

    def inverse_invariant_potential(
        self,
        substitute=False,
        interval=sp.Reals,
        simplify=False,
        # method="solve",
        assume_scalar_field_positive=False,
        solve_kwargs={"force": True},
        params={},
    ):
        if not isinstance(self.V, InflationFunction):
            raise TypeError(f"V function must be InflationFunction type. {type(self.V)}")
        if not isinstance(self.A, InflationFunction):
            raise TypeError(f"A function must be InflationFunction type. {type(self.A)}")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(f"I_V function must be InflationFunction type. {type(self.I_V)}")

        if self.mp is None or self.I_V is None:
            raise ValueError("Planck's mass symbol on invariant potenttial not defined.")
        if substitute:
            if self.A is None or self.V is None:
                raise ValueError("Cant make substitution if A and V function not defined.")

        symbolI = (
            self.symbolI
            if not assume_scalar_field_positive
            else sp.Symbol(str(self.symbolI), real=True, positive=True)
        )

        analytical_function = self.I_V.f_s(params) - self.IV_symbol
        analytical_function = analytical_function.subs(self.symbolI, symbolI)

        # if method == "solveset":
        #     solutions = sp.solveset(analytical_function, symbolI, domain=interval)
        #     if isinstance(solutions, sp.Union):
        #         print("Solution is some union. Specify interval.")
        #         display(solutions)
        #         return
        #     elif isinstance(solutions, sp.sets.sets.EmptySet):
        #         print("Couldn't find any solutions")
        #         return
        #     elif isinstance(solutions, sp.sets.conditionset.ConditionSet):
        #         print(
        #             "Solution is expressed as some condition. Sympy might not have found the inverse function. If possible, define solution(s) manually."
        #         )
        #         display(solutions)
        #         return
        #     elif isinstance(solutions, sp.Intersection):
        #         possible_solutions = solutions.args[-1]
        #         if isinstance(possible_solutions, sp.FiniteSet):
        #             result = self._get_sym_solution_from_finiteset(solutions)
        #             print(
        #                 "Solution is expressed as intersection. Solution might be wrongly interpreted. Might need to define solution(s) manually."
        #             )
        #         else:
        #             print("Couldn't interpret solution(s). Please add solution(s) manually.")
        #             display(solutions)
        #             return
        #         display(solutions)
        #     elif isinstance(solutions, sp.FiniteSet):
        #         result = self._get_sym_solution_from_finiteset(solutions)
        #     else:
        #         NotImplementedError("Got unexpected type of solutions.")
        # elif method == "solve":
        result = list(sp.solve(analytical_function, symbolI, **solve_kwargs))  # type: ignore
        # else:
        #     raise ValueError("Solve method can only be 'solve' or 'solveset'.")

        if substitute:
            result = [x.subs(self.IV_symbol, self.V.f_s(params) / self.A.f_s(params) ** 2) for x in result]

        if simplify:
            result = [sp.simplify(x, inverse=True) for x in result]

        # Sort such that solutions which have imaginary in will be last
        result.sort(key=lambda x: x.has(sp.I))

        return result

    def solve_invariant_field(self, assume_scalar_field_positive=False):
        if not isinstance(self.B, InflationFunction):
            raise TypeError(f"B function must be InflationFunction type. {type(self.B)}")
        if not isinstance(self.A, InflationFunction):
            raise TypeError(f"A function must be InflationFunction type. {type(self.A)}")

        symbol = (
            self.symbol if not assume_scalar_field_positive else sp.Symbol(str(self.symbol), real=True, positive=True)
        )

        if self.palatini:
            integrand = sp.sqrt(self.B.f_s() / self.A.f_s())
        else:
            integrand = sp.sqrt(
                self.B.f_s() / self.A.f_s() + sp.Rational(3, 2) * self.mp**2 * (self.A.fd_s() / self.A.f_s()) ** 2
            )
        if assume_scalar_field_positive:
            integrand = integrand.subs(self.symbol, symbol)

        integral = sp.integrate(integrand, symbol)

        if isinstance(integral, sp.Integral):
            display(integral)
            raise RuntimeError("Couldn't integrate given function.")
        if assume_scalar_field_positive:
            integral = integral.subs(symbol, self.symbol)

        return integral

    def nsolve_field_mp(self, x, y0, invariant=True, sign="+", solver=None, params={}, mp_kwargs={}):
        """
        Numerically calculate funtion Invariant field(field) or field(Invariant field).

        Parameters
        ----------
        x : np.array, list
            Values for scalar field (if invariant=True) / invariant scalar field (if invariant = False)
        y0 : _type_
            Initial condition. Value for scalar field (if invariant=False) / invariant scalar field (if invariant = True)
        invariant : bool, optional
            If invariant is True then result function is invariant scalar field. Else result is scalar field, by default True
        solver : _type_, optional
            Used defined solver. Input in form (integrand, x_0, y0, x_f, *args, **kwargs) where integrand is function dy/dt and takes in two inputs (t, y). Not required. by default None
        params : dict, optional
            Dictionary of symbol-value pairs. All free symbols (except scalar invariant field) must have an assigned value, by default {}

        Returns
        -------
        Callable
            Returns interpolation of calculated function. For evaluation uses points given in x. Input must be between x[0] and x[-1].
        """
        if not isinstance(self.F, InflationFunction):
            raise TypeError(
                f"A or B function is not defined. F function must be InflationFunction type. ({type(self.F)})"
            )

        params = _check_params([self.F.f_s()], [self.symbol], params)
        if not isinstance(x, (np.ndarray, list)):
            raise TypeError(f"x must be list or np.ndarray tpye ({type(x)}).")
        if not len(x) == 2:
            raise ValueError("X must be an array/list of length two.")

        if sign == "+":
            sign = 1
        elif sign == "-":
            sign = -1
        else:
            raise ValueError("sign must be '+' or '-'.")

        if invariant:
            function = sp.lambdify(self.symbol, sign * sp.sqrt(self.F.f_s(params)), "mpmath")
        else:
            function = sp.lambdify(self.symbol, sign * 1 / sp.sqrt(self.F.f_s(params)), "mpmath")

        x_0 = x[0]
        x_f = x[-1]

        if x_0 == x_f:
            raise ValueError("Initial value can't equal to final value.")

        if solver is None:
            if x_0 > x_f:
                if invariant:
                    function_n = lambda phi, Iphi: function(-phi)
                else:
                    function_n = lambda Iphi, phi: function(phi)
                phi_function = mp.odefun(function_n, -x_0, y0, **mp_kwargs)
                phi_function(-x_f)
                result = lambda z: phi_function(-z)
                return result
            else:
                if invariant:
                    function_n = lambda phi, Iphi: function(phi)
                else:
                    function_n = lambda Iphi, phi: function(phi)
                phi_function = mp.odefun(function_n, x_0, y0, **mp_kwargs)
                phi_function(x_f)
                return phi_function
        else:
            if invariant:
                function_n = lambda phi, Iphi: function(phi)
            else:
                function_n = lambda Iphi, phi: function(phi)
            solver(function_n, x_0, y0, x_f)

    def nsolve_field_np(self, x, y0, invariant=True, sign="+", solver=None, params={}, sc_kwargs={}):
        """
        Numerically calculate funtion Invariant field(field) or field(Invariant field).

        Parameters
        ----------
        x : np.array, list
            Values for scalar field (if invariant=True) / invariant scalar field (if invariant = False)
        y0 : _type_
            Initial condition. Value for scalar field (if invariant=False) / invariant scalar field (if invariant = True)
        invariant : bool, optional
            If invariant is True then result function is invariant scalar field. Else result is scalar field, by default True
        solver : _type_, optional
            Used defined solver. Input in form (integrand, x_0, y0, x_f, *args, **kwargs) where integrand is function dy/dt and takes in two inputs (t, y). Not required. by default None
        params : dict, optional
            Dictionary of symbol-value pairs. All free symbols (except scalar invariant field) must have an assigned value, by default {}

        Returns
        -------
        Callable
            Returns interpolation of calculated function. For evaluation uses points given in x. Input must be between x[0] and x[-1].
        """
        if not isinstance(self.F, InflationFunction):
            raise TypeError(
                f"A or B function is not defined. F function must be InflationFunction type. ({type(self.F)})"
            )

        params = _check_params([self.F.f_s()], [self.symbol], params)

        if not isinstance(x, (np.ndarray, list)):
            raise TypeError(f"x must be list or np.ndarray tpye ({type(x)}).")
        else:
            x = np.array(x, dtype=float)
        if not len(x) >= 2:
            raise ValueError("X must be an array/list of length at least two.")

        if sign == "+":
            sign = 1
        elif sign == "-":
            sign = -1
        else:
            raise ValueError("sign must be '+' or '-'.")

        if invariant:
            function = sp.lambdify(self.symbol, sign * sp.sqrt(self.F.f_s(params)), "mpmath")
        else:
            function = sp.lambdify(self.symbol, sign * 1 / sp.sqrt(self.F.f_s(params)), "mpmath")

        x_0 = x[0]
        x_f = x[-1]

        if x_0 == x_f:
            raise ValueError("Initial value can't equal to final value.")

        if invariant:
            function_n = lambda phi, Iphi: function(phi)
        else:
            function_n = lambda Iphi, phi: function(phi)

        if solver is None:
            if sc_kwargs.get("method", None) is None:
                sc_kwargs["method"] = "LSODA"

            ode = solve_ivp(
                function_n, t_span=[float(x[0]), float(x[-1])], y0=[float(y0)], dense_output=True, **sc_kwargs
            )
            if ode.status == -1:
                raise RuntimeError(f"Integration step failed. (scipy ode solver)\n{ode.message}")
            elif ode.status == 1:
                raise RuntimeError(f"A termination event occurred. (scipy ode solver)\n{ode.message}")
            # phi_function = interp1d(x, ode.y.reshape(-1))
            phi_function = lambda y: ode.sol(y).reshape(-1)
            return phi_function
        else:
            solver(function_n, x_0, y0, x_f)

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

    def _return_ordered_symbols(self, function) -> List[sp.Symbol]:
        """Returns given function all free variables in a sorted order.
        Scalar field value is first, Planck's mass value is second and then follows alphabetical order.

        Parameters
        ----------
        function : _type_
            _description_

        Returns
        -------
        List[sp.Symbol]
            _description_
        """
        if isinstance(function, InflationFunction):
            symbols = list(function.free_symbols() - {self.symbol})
        elif isinstance(function, sp.Expr):
            symbols = list(function.free_symbols - {self.symbol})
        symbols.sort(key=lambda x: str(x).lower())
        if self.mp in symbols:
            # Take from current index and put it as first
            symbols.insert(0, symbols.pop(symbols.index(self.mp)))
        result = [self.symbol, *symbols]
        self._sorted_variables = result
        return result


class FunctionAsolver(FunctionSolver):
    def __init__(
        self,
        model: Optional[SlowRollModel] = None,
    ) -> None:
        super().__init__(model)
        if not isinstance(self.B, InflationFunction):
            raise TypeError(f"B function must be InflationFunction type. ({type(self.B)})")
        if not isinstance(self.V, InflationFunction):
            raise TypeError(f"V function must be InflationFunction type. ({type(self.V)})")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(f"I_V function must be InflationFunction type. ({type(self.I_V)})")

        self.inverse_symbol_dif = sp.Symbol(
            f"\\frac{{dI_{sp.latex(self.symbol)}}}{{d{sp.latex(self.symbol)}}}", real=True
        )

        if self.palatini:
            self.A_dif_element1 = sp.Rational(1, 2) * self.A_symbol * self.V.fd_s() / self.V.f_s()
            self.A_dif_element2 = (
                sp.Rational(1, 2)
                * self.A_symbol**2
                * sp.Abs(self.V.f_s() / self.inverse_symbol_dif)
                * sp.sqrt(self.A_symbol * self.B.f_s())
                / self.V.f_s() ** 2
            )
        else:
            self.A_dif_element1 = (
                4
                * self.A_symbol
                * self.V.f_s()
                * self.V.fd_s()
                / (8 * self.V.f_s() ** 2 - 3 * self.mp**2 * self.A_symbol**4 / self.inverse_symbol_dif**2)
            )
            self.A_dif_element2 = (
                sp.Abs(1 / self.inverse_symbol_dif)
                * sp.sqrt(
                    16 * self.A_symbol**5 * self.B.f_s() * self.V.f_s() ** 2
                    + 6
                    * self.mp**2
                    * self.A_symbol**6
                    * (self.V.fd_s() ** 2 - self.A_symbol**3 * self.B.f_s() / self.inverse_symbol_dif**2)
                )
                / (8 * self.V.f_s() ** 2 - 3 * self.mp**2 * self.A_symbol**4 / self.inverse_symbol_dif**2)
            )

    def solve(
        self,
        invariant_potential_inverse: Union[sp.Expr, InflationFunction, int, float],
        sign="plus",
        params={},
    ):
        if not (self.V, InflationFunction):
            raise TypeError(f"V function not defined. V function must be InflationFunction type. {type(self.V)}")

        params = {str(key): value for key, value in params.items()}
        if isinstance(invariant_potential_inverse, (sp.Expr, float, int)):
            if isinstance(invariant_potential_inverse, (float, int)):
                invariant_potential_inverse = sp.N(invariant_potential_inverse)
            inverse_dif = sp.diff(invariant_potential_inverse, self.IV_symbol).subs(
                self.IV_symbol, self.V.f_s() / self.A_symbol**2
            )
        elif isinstance(invariant_potential_inverse, InflationFunction):
            inverse_dif = invariant_potential_inverse.fd_s().subs(
                invariant_potential_inverse.symbol, self.V.f_s() / self.A_symbol**2
            )
        else:
            raise TypeError("inverse function is wrong type.")

        if sign in ["plus", "+"]:
            # A_dif = (self.A_dif_numerator1 + self.A_dif_numerator2) / self.A_dif_denominator
            A_dif = self.A_dif_element1 + self.A_dif_element2
        elif sign in ["minus", "-"]:
            # A_dif = (self.A_dif_numerator1 - self.A_dif_numerator2) / self.A_dif_denominator
            A_dif = self.A_dif_element1 - self.A_dif_element2
        else:
            raise ValueError('sign value can only be "plus"/"+" or "minus"/"-".')

        free_symbols = A_dif.free_symbols - {self.symbol, self.A_symbol}
        free_variable_values = {key: params.get(str(key)) for key in list(free_symbols)}

        A_dif = A_dif.subs(self.inverse_symbol_dif, inverse_dif)
        A_dif = A_dif.subs(free_variable_values)

        return A_dif

    def get_nfun(
        self,
        invariant_potential_inverse,
        sign,
        mpmath: bool = False,
        params={},
    ):
        assert isinstance(self.V, InflationFunction), "V function not InflationFunction type"

        if isinstance(invariant_potential_inverse, sp.Expr):
            inverse_dif = sp.diff(invariant_potential_inverse, self.IV_symbol).subs(
                self.IV_symbol, self.V.f_s() / self.A_symbol**2
            )
        elif isinstance(invariant_potential_inverse, InflationFunction):
            inverse_dif = invariant_potential_inverse.fd_s().subs(
                invariant_potential_inverse.symbol, self.V.f_s() / self.A_symbol**2
            )
        else:
            raise TypeError("inverse function type can only be sp.Expr or InflationFunction.")

        if sign == "plus" or sign == "+":
            # A_dif = (self.A_dif_numerator1 + self.A_dif_numerator2) / self.A_dif_denominator
            A_dif = self.A_dif_element1 + self.A_dif_element2
        elif sign == "minus" or sign == "-":
            # A_dif = (self.A_dif_numerator1 - self.A_dif_numerator2) / self.A_dif_denominator
            A_dif = self.A_dif_element1 - self.A_dif_element2
        else:
            raise ValueError('sign value can only be "plus"/"+" or "minus"/"-".')
        A_dif = A_dif.subs(self.inverse_symbol_dif, inverse_dif)

        params = _check_params([A_dif], [self.symbol, self.A_symbol], params)

        A_dif = A_dif.subs(params)
        if mpmath:
            function = sp.lambdify((self.symbol, self.A_symbol), A_dif, "mpmath")
        else:
            function = sp.lambdify((self.symbol, self.A_symbol), A_dif, "scipy")

        return function

    def nsolve_mp(
        self,
        invariant_potential_inverse: Union[sp.Expr, InflationFunction],
        x: Union[List[Union[float, int, mp.mpf]], np.ndarray],
        y0,
        sign: str,
        solver=None,
        params={},
        mp_kwargs={},
    ):
        if not isinstance(x, list):
            raise TypeError("x must be a list type.")
        if not len(x) == 2:
            raise ValueError("x list can contain only initial and final value.")
        x_0 = x[0]
        x_f = x[-1]

        if x_0 == x_f:
            raise ValueError("Initial and final value can't be equal.")
        function = self.get_nfun(
            invariant_potential_inverse=invariant_potential_inverse,
            sign=sign,
            mpmath=True,
            params=params,
        )
        if solver is None:
            result_function = self._numeric_solver_mp1(function, x_0, y0, x_f, **mp_kwargs)
        else:
            result_function = solver(function, x_0, y0, x_f)

        return result_function

    def _numeric_solver_mp1(self, fn, x0, y0, x_end, **kwargs):
        """
        If x0 < x_end then mpmath can't solve differential equation.
        Then problem must be defined such that mpmath can solve:
        f(x, y) -> -f(-x, y)
        """
        if x0 > x_end:
            new_fn = lambda x, y: -fn(-x, y)
            result_function = mp.odefun(new_fn, -x0, y0, **kwargs)
            result_function(-x_end)
            return lambda z: result_function(-z)
        else:
            result_function = mp.odefun(fn, x0, y0, **kwargs)
            result_function(x_end)
            return result_function

    def nsolve_np(
        self,
        invariant_potential_inverse: Union[sp.Expr, InflationFunction],
        x: Union[List[Union[float, int, mp.mpf]], np.ndarray],
        y0,
        sign: str,
        solver=None,
        params={},
        sc_kwargs={},
    ):
        if not isinstance(x, (list, np.ndarray)):
            raise TypeError("x must be a list or np.ndarray type.")
        if isinstance(x, list):
            x = np.array(x, dtype=float)

        x_0 = x[0]
        x_f = x[-1]

        if x_0 == x_f:
            raise ValueError("Initial and final value can't be equal.")

        function = self.get_nfun(
            invariant_potential_inverse=invariant_potential_inverse,
            sign=sign,
            mpmath=False,
            params=params,
        )
        if solver is None:
            result_function = self._numeric_solver_np1(function, x_0, y0, x_f, x, **sc_kwargs)
        else:
            result_function = solver(function, x_0, y0, x_f)
        return result_function

    def _numeric_solver_np1(self, fn, x0, y0, x_end, x_eval, **kwargs):
        fun = lambda x, y: fn(x, y)
        if x_eval is None:
            x_eval = np.linspace(x0, x_end, 1000)
        if kwargs.get("method", None) is None:
            kwargs["method"] = "LSODA"

        ode = solve_ivp(fun, t_span=[float(x0), float(x_end)], y0=[float(y0)], dense_output=True, **kwargs)
        if ode.status == -1:
            raise RuntimeError(f"Integration step failed. (scipy ode solver)\n{ode.message}")
        elif ode.status == 1:
            raise RuntimeError(f"A termination event occurred. (scipy ode solver)\n{ode.message}")
        # A_function = interp1d(x_eval, ode.y.reshape(-1))
        A_function = lambda y: ode.sol(y).reshape(-1)
        return A_function

    def return_initial_condition(self, invariant_end_value=None, field_value=None, params={}):
        if not isinstance(self.V, InflationFunction):
            raise TypeError(f"V function not defined. V function must be InflationFunction type. {type(self.V)}")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(
                f"Invariant potential not defined. I_V function must be InflationFunction type. {type(self.I_V)}"
            )

        functions_to_check = [self.V.f_s(), self.I_V.f_s()]

        if isinstance(invariant_end_value, sp.Expr):
            functions_to_check.append(invariant_end_value)
        if isinstance(field_value, sp.Expr):
            functions_to_check.append(field_value)

        variables = set()
        for elem in functions_to_check:
            variables = variables.union(elem.free_symbols)

        variable_dict = {str(variable): variable for variable in variables}
        params = {str(x): value for x, value in params.items() if str(x) in variable_dict.keys()}
        parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}
        return (
            sp.sqrt(self.V.f_s() / self.I_V.f_s())
            .subs(self.symbolI, invariant_end_value)
            .subs(self.symbol, field_value)
            .subs(parameters)
        )

    def return_initial_condition_np(self, invariant_end_value, field_value, params={}):
        if not isinstance(self.V, InflationFunction):
            raise TypeError(f"V function not defined. V function must be InflationFunction type. {type(self.V)}")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(
                f"Invariant potential not defined. I_V function must be InflationFunction type. {type(self.I_V)}"
            )
        functions_to_check = [self.V.f_s(), self.I_V.f_s()]

        if isinstance(invariant_end_value, sp.Expr):
            functions_to_check.append(invariant_end_value)
        if isinstance(field_value, sp.Expr):
            functions_to_check.append(field_value)

        params = _check_params(functions_to_check, [self.symbol, self.symbolI], params)

        value = self.return_initial_condition(invariant_end_value, field_value, params)
        return float(sp.N(value, mp.mp.dps))

    def return_initial_condition_mp(self, invariant_end_value, field_value, params={}):
        if not isinstance(self.V, InflationFunction):
            raise TypeError(f"V function not defined. V function must be InflationFunction type. {type(self.V)}")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(
                f"Invariant potential not defined. I_V function must be InflationFunction type. {type(self.I_V)}"
            )

        functions_to_check = [self.V.f_s(), self.I_V.f_s()]

        if isinstance(invariant_end_value, sp.Expr):
            functions_to_check.append(invariant_end_value)
        if isinstance(field_value, sp.Expr):
            functions_to_check.append(field_value)

        params = _check_params(functions_to_check, [self.symbol, self.symbolI], params)

        value = self.return_initial_condition(invariant_end_value, field_value, params)
        return mp.convert(sp.N(value, mp.mp.dps))


class FunctionBsolver(FunctionSolver):
    def __init__(self, model: Optional[SlowRollModel] = None) -> None:
        super().__init__(model)
        if not isinstance(self.A, InflationFunction):
            raise TypeError(f"A function must be InflationFunction type. ({type(self.A)})")
        if not isinstance(self.V, InflationFunction):
            raise TypeError(f"V function must be InflationFunction type. ({type(self.V)})")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(f"I_V function must be InflationFunction type. ({type(self.I_V)})")

    def solve(
        self,
        invariant_potential_inverse: Union[sp.Expr, int, float, InflationFunction],
        assume_scalar_field_positive=False,
        substitute=True,
        params={},
    ):
        assert isinstance(self.A, InflationFunction), "Function A not InflationFunction type"
        assert isinstance(self.V, InflationFunction), "Function V not InflationFunction type"

        params = {str(key): value for key, value in params.items()}
        symbol = (
            self.symbol if not assume_scalar_field_positive else sp.Symbol(str(self.symbol), real=True, positive=True)
        )
        if substitute:
            if isinstance(invariant_potential_inverse, (sp.Expr, int, float)):
                if isinstance(invariant_potential_inverse, (int, float)):
                    invariant_potential_inverse = sp.N(invariant_potential_inverse)
                invariant_potential_inverse = invariant_potential_inverse.subs(
                    self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2
                )
            elif isinstance(invariant_potential_inverse, InflationFunction):
                invariant_potential_inverse = invariant_potential_inverse.f_s().subs(
                    self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2
                )
            else:
                raise TypeError("inverse function is wrong type.")

        assert isinstance(
            invariant_potential_inverse, sp.Expr
        ), "invariant_potential_inverse not sp.Expr type during calculation"

        A_fun = self.A.f_s()
        A_der = self.A.fd_s()

        if assume_scalar_field_positive:
            invariant_potential_inverse = invariant_potential_inverse.subs(self.symbol, symbol)
            A_fun = A_fun.subs(self.symbol, symbol)
            A_der = A_der.subs(self.symbol, symbol)

        inverse_derivative = sp.diff(invariant_potential_inverse, symbol)
        if self.palatini:
            B = A_fun * inverse_derivative**2
        else:
            B = A_fun * (inverse_derivative**2 - sp.Rational(3, 2) * self.mp**2 * (A_der / A_fun) ** 2)

        if assume_scalar_field_positive:
            B = B.subs(symbol, self.symbol)

        free_symbols = B.free_symbols - {self.symbol}
        free_variable_values = {key: params.get(str(key)) for key in list(free_symbols)}
        B = B.subs(free_variable_values)

        return InflationFunction(B, symbol=self.symbol, mp=self.mp)

    def nsolve_mp(
        self,
        invariant_potential_inverse: Union[sp.Expr, InflationFunction, float, int],
        x: Union[List[Union[float, int, mp.mpf]], np.ndarray],
        substitute=True,
        params={},
    ):
        assert isinstance(self.A, InflationFunction), "Function A not InflationFunction type"
        assert isinstance(self.V, InflationFunction), "Function V not InflationFunction type"

        if isinstance(invariant_potential_inverse, (float, int)):
            invariant_potential_inverse = sp.N(invariant_potential_inverse)
        elif isinstance(invariant_potential_inverse, InflationFunction):
            invariant_potential_inverse = invariant_potential_inverse.f_s()
        elif not isinstance(invariant_potential_inverse, sp.Expr):
            raise TypeError(
                "Invariant potential inverse function must be type of int, float, sp.Expr or InflationFunction."
            )

        assert isinstance(
            invariant_potential_inverse, sp.Expr
        ), "invariant_potential_inverse not sp.Expr type during calculation"

        params = _check_params(
            [self.A.f_s(), self.V.f_s(), invariant_potential_inverse], [self.symbol, self.IV_symbol], params
        )
        if substitute:
            invariant_potential_inverse = invariant_potential_inverse.subs(
                self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2
            )
        inverse_derivative = sp.diff(invariant_potential_inverse, self.symbol)
        if self.palatini:
            sym_function = self.A.f_s() * inverse_derivative**2
        else:
            sym_function = self.A.f_s() * (
                inverse_derivative**2 - sp.Rational(3, 2) * self.mp**2 * (self.A.fd_s() / self.A.f_s()) ** 2
            )
        sym_function = sym_function.subs(params)
        function = sp.lambdify(self.symbol, sym_function, "mpmath")

        if isinstance(x, Iterable):
            return [function(y) for y in x]
        else:
            return function(x)

    def nsolve_np(
        self,
        invariant_potential_inverse: Union[sp.Expr, InflationFunction, float, int],
        x: Union[List[Union[float, int, mp.mpf]], np.ndarray],
        substitute=True,
        params={},
    ):
        assert isinstance(self.A, InflationFunction), "Function A not InflationFunction type"
        assert isinstance(self.V, InflationFunction), "Function V not InflationFunction type"

        if isinstance(invariant_potential_inverse, (float, int)):
            invariant_potential_inverse = sp.N(invariant_potential_inverse)
        elif isinstance(invariant_potential_inverse, InflationFunction):
            invariant_potential_inverse = invariant_potential_inverse.f_s()
        elif not isinstance(invariant_potential_inverse, sp.Expr):
            raise TypeError(
                "Invariant potential inverse function must be type of int, float, sp.Expr or InflationFunction."
            )

        assert isinstance(
            invariant_potential_inverse, sp.Expr
        ), "invariant_potential_inverse not sp.Expr type during calculation"

        params = _check_params(
            [self.A.f_s(), self.V.f_s(), invariant_potential_inverse], [self.symbol, self.IV_symbol], params
        )
        if substitute:
            invariant_potential_inverse = invariant_potential_inverse.subs(
                self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2
            )
        inverse_derivative = sp.diff(invariant_potential_inverse, self.symbol)
        if self.palatini:
            sym_function = self.A.f_s() * inverse_derivative**2
        else:
            sym_function = self.A.f_s() * (
                inverse_derivative**2 - sp.Rational(3, 2) * self.mp**2 * (self.A.fd_s() / self.A.f_s()) ** 2
            )
        sym_function = sym_function.subs(params)
        function = sp.lambdify(self.symbol, sym_function, "scipy")
        interval = np.array(x, dtype=float)
        result = function(interval)
        if isinstance(interval, np.ndarray) and isinstance(result, (int, float)):
            result = np.full(interval.shape, result)
        return result

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


class FunctionVsolver(FunctionSolver):
    def __init__(
        self,
        model: Optional[SlowRollModel] = None,
    ) -> None:
        super().__init__(model)
        if not isinstance(self.A, InflationFunction):
            raise TypeError(f"A function must be InflationFunction type. ({type(self.A)})")
        if not isinstance(self.B, InflationFunction):
            raise TypeError(f"B function must be InflationFunction type. ({type(self.B)})")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(f"I_V function must be InflationFunction type. ({type(self.I_V)})")

        if self.palatini:
            self.integrand = InflationFunction(
                sp.sqrt(self.B.f_s() / self.A.f_s()), symbol=self.symbol, mp=self.mp, positive=self.A.positive
            )
        else:
            self.integrand = InflationFunction(
                sp.sqrt(
                    self.B.f_s() / self.A.f_s()
                    - sp.Rational(3, 2) * self.mp**2 * (self.A.fd_s() / self.A.f_s()) ** 2
                ),
                symbol=self.symbol,
                mp=self.mp,
                positive=self.A.positive,
            )

    def solve(self, invariant_scalar_field: sp.Expr, params={}):
        assert isinstance(self.A, InflationFunction), "Function A not InflationFunction type"
        assert isinstance(self.I_V, InflationFunction), "Function I_V not InflationFunction type"

        V = (self.I_V.f_s().subs(self.I_V.symbol, invariant_scalar_field)) * self.A.f_s() ** 2

        variables = V.free_symbols
        variable_dict = {str(variable): variable for variable in variables}
        params = {str(x): value for x, value in params.items() if str(x) in variable_dict.keys()}
        parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}

        V = V.subs(parameters)

        return InflationFunction(V, symbol=self.symbol, mp=self.mp)

    def nsolve_mp(
        self,
        invariant_scalar_field: Optional[Union[sp.Expr, InflationFunction, Callable]],
        x: [np.ndarray, list],
        params={},
    ):
        assert isinstance(self.A, InflationFunction), "Function A not InflationFunction type"
        assert isinstance(self.I_V, InflationFunction), "Function I_V not InflationFunction type"

        if isinstance(invariant_scalar_field, InflationFunction):
            invariant_scalar_field = invariant_scalar_field.f_s()

        if isinstance(invariant_scalar_field, sp.Expr):
            params = _check_params(
                [self.A.f_s(), invariant_scalar_field, self.I_V.f_s()], [self.symbol, self.symbolI], params
            )
        else:
            assert isinstance(self.B, InflationFunction), "Function B not InflationFunction type"
            params = _check_params([self.A.f_s(), self.B.f_s(), self.I_V.f_s()], [self.symbol, self.symbolI], params)

        # If invariant scalar field is defined we can take a shortcut:
        A = self.A(params)
        IV = self.I_V(params)
        if isinstance(invariant_scalar_field, Callable):
            if isinstance(x, Iterable):
                return [
                    IV.f_n(invariant_scalar_field(mp.convert(y)), mode="mpmath")
                    * A.f_n(mp.convert(y), mode="mpmath") ** 2
                    for y in x
                ]
            else:
                return (
                    IV.f_n(invariant_scalar_field(mp.convert(x)), mode="mpmath")
                    * A.f_n(mp.convert(x), mode="mpmath") ** 2
                )
        elif isinstance(invariant_scalar_field, sp.Expr):
            V = (IV.f_s().subs(IV.symbol, invariant_scalar_field)) * A.f_s() ** 2
            V = V.subs(params)
            function = sp.lambdify(A.symbol, V, "mpmath")
            if isinstance(x, Iterable):
                return [function(mp.convert(y)) for y in x]
            else:
                return function(mp.convert(x))
        else:
            raise TypeError("Invariant scalar field can be Callable, sp.Expr or InflationFunction type.")

    def nsolve_np(
        self,
        invariant_scalar_field: Optional[Union[sp.Expr, InflationFunction, Callable]],
        x: Union[np.ndarray, list],
        params={},
    ):
        assert isinstance(self.A, InflationFunction), "Function A not InflationFunction type"
        assert isinstance(self.I_V, InflationFunction), "Function I_V not InflationFunction type"
        x = np.array(x, dtype=float)
        if isinstance(invariant_scalar_field, InflationFunction):
            invariant_scalar_field = invariant_scalar_field.f_s()

        if isinstance(invariant_scalar_field, sp.Expr):
            params = _check_params(
                [self.A.f_s(), invariant_scalar_field, self.I_V.f_s()], [self.symbol, self.symbolI], params
            )
        else:
            assert isinstance(self.B, InflationFunction), "Function B not InflationFunction type"
            params = _check_params([self.A.f_s(), self.B.f_s(), self.I_V.f_s()], [self.symbol, self.symbolI], params)

        # If invariant scalar field is defined we can take a shortcut:

        A = self.A(params)
        IV = self.I_V(params)
        if isinstance(invariant_scalar_field, Callable):
            result = IV.f_n(invariant_scalar_field(x)) * A.f_n(x) ** 2
            if isinstance(x, np.ndarray) and isinstance(result, (int, float)):
                result = np.full(x.shape, result)
            return result
        elif isinstance(invariant_scalar_field, sp.Expr):
            V = (IV.f_s().subs(IV.symbol, invariant_scalar_field)) * A.f_s() ** 2
            V = V.subs(params)
            function = sp.lambdify(self.symbol, V, "scipy")
            result = function(x)
            if isinstance(x, np.ndarray) and isinstance(result, (int, float)):
                result = np.full(x.shape, result)
            return result
        else:
            raise TypeError("Invariant scalar field can be None, Callable, sp.Expr or InflationFunction type.")
