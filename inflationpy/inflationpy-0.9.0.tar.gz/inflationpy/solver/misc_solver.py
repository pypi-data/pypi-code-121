from typing import Optional, Type, Union, List, Callable, Iterable

import numpy as np
import sympy as sp
import scipy as sc
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.misc import derivative
import mpmath as mp

from IPython.display import display

from inflationpy.core.functions import InflationFunction
from inflationpy.core.model import SlowRollModel


def _check_params(functions: List[sp.Expr], remove_symbols: List[sp.Symbol], params={}, raise_excess_error=True):
    """
    Takes in a list of funtions and finds all free symbols. Then excludes given symbols.
    Match symbols then to form pairs where key is sp.Symbol type and value is given symbol value.
    If raise_excess_error is True then raise ValueError of found free symbols set is not subset of set from symbols in params.

    Used to convert all keys in params to sp.Symbol types as key can be string as well. To assure that all flags for symbols are correct we use given function symbols.

    Parameters
    ----------
    functions : List[sp.Expr]
        List of functions
    remove_symbols : List[sp.Symbol]
        List of symbols to exclude from free symbols set
    params : dict
        symbol: value pairs, by default {}
    raise_excess_error : bool, optional
        Boolean if to Raise ValueError when set of free symbols is not subset of symbols from params, by default True

    Returns
    -------
    dict
        {sp.Symbol: symbol value} pairs

    """
    params = {str(key): value for key, value in params.items()}
    free_symbols = set()
    for func in functions:
        if isinstance(func, sp.Expr):
            free_symbols = free_symbols.union(func.free_symbols)
    free_symbols = free_symbols - set(remove_symbols)
    if raise_excess_error:
        excess_parameters = set([str(x) for x in free_symbols]).difference(set(params.keys()))
        if excess_parameters != set():
            raise ValueError(
                f"Some free parameters are not defined. Cannot calculate numerically. ({', '.join(list(excess_parameters))})"
            )
    free_variable_values_dict = {key: params.get(str(key)) for key in list(free_symbols)}
    return free_variable_values_dict


class BaseSolver:
    def __init__(self, model: Optional[SlowRollModel] = None):
        if not isinstance(model, SlowRollModel):
            raise TypeError("Inserted function must be SlowRollModel type.")
        else:
            self.mp = model.mp
            self.symbol = model.symbol
            self.symbolI = model.symbolI
            self.A = model.A
            self.B = model.B
            self.V = model.V
            self.I_V = model.I_V
            self.F = model.F
            self.palatini = model.palatini

        self.IV_symbol = sp.Symbol("I_V", real=True)
        self.A_symbol = sp.Symbol("A", real=True, positive=True)
        self.B_symbol = sp.Symbol("B", real=True)
        self.V_symbol = sp.Symbol("V", real=True)

    def solve_invariant_field(self, params={}):
        """
        Calculates Invariant scalar field function using definition between invariant scalar field and scalar field.

        Returns
        -------
        sp.Expr
            I_phi(phi) function. Where phi is scalar field.
        """
        try:
            assert isinstance(self.F, InflationFunction)
        except:
            raise TypeError(f"F function type must be InflationFunction ({type(self.F)}).")

        result = sp.integrate(sp.sqrt(self.F.f_s(params)), self.symbol)
        if isinstance(result, sp.Integral):
            display(result)
            raise RuntimeError("Couldn't integrate I_phi function.")

        return result

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

    def solve_I_V_inverse(
        self,
        substitute=False,
        simplify=False,
        assume_scalar_field_positive=True,
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
        result = list(sp.solve(analytical_function, symbolI, **solve_kwargs))  # type: ignore

        if substitute:
            result = [x.subs(self.IV_symbol, self.V.f_s(params) / self.A.f_s(params) ** 2) for x in result]

        if simplify:
            result = [sp.simplify(x, inverse=True) for x in result]

        # Sort such that solutions which have imaginary in will be last
        result.sort(key=lambda x: x.has(sp.I))

        return result


class NFoldCorrection(BaseSolver):
    def __init__(self, model: Optional[SlowRollModel] = None):
        super().__init__(model)

        if not isinstance(self.A, InflationFunction):
            raise TypeError(f"A function must be InflationFunction type. ({type(self.A)})")
        if not isinstance(self.B, InflationFunction):
            raise TypeError(f"B function must be InflationFunction type. ({type(self.B)})")

    def correction(self, initial_value, end_value, mode="numpy", params={}):
        """Caluclates N-fold difference between Jordan and Einstein frame.

        Parameters
        ----------
        initial_value : float, mp.mpf, sp.Expr
            Initial value for scalar field in Jordan frame.
        end_value : float, mp.mpf, sp.Expr
            End value for scalar field in Jordan frame.
        mode : str, optional
            What mode to use for calculation and what format will be returned "numpy"
        params : dict, optional
            Free parameter values, by default {}

        Returns
        -------
        _type_
            _description_
        """
        try:
            assert isinstance(self.A, InflationFunction)
        except:
            raise TypeError("A function type is wrong.")

        correction_value = sp.Rational(1, 2) * sp.log(
            self.A.f_s(params).subs(self.symbol, end_value) / self.A.f_s(params).subs(self.symbol, initial_value)
        )
        params = _check_params([self.A.f_s()], [self.symbol], params)

        if mode in ["numpy", "scipy"]:
            return float(correction_value)
        elif mode == "mpmath":
            return mp.convert(sp.N(correction_value, mp.mp.dps))
        elif mode == "sympy":
            return correction_value

        else:
            raise ValueError("Mode can be 'numpy'/'scipy' or 'mpmath'.")

    def solve_field(self, Iphi=None, simplify=False, solve_kwargs={"force": True}):
        """
        Calculates function field(Invariant field) using definition of Invariant field(field).
        If invariant field is not given then also tries to calculate invariant field integral.

        Parameters
        ----------
        Iphi : sp.Expr
            Invariant scalar field function which is calculated from it's definition, by default None
        simplify : bool, optional
            To simplify result, by default False
        solve_kwargs : dict, optional
            Sympy .solve() method kwargs, by default {"force": True}

        Returns
        -------
        list[sp.Expr]
            Invariant scalar field's inverse function(s).
        """
        if Iphi is None:
            Iphi = self.solve_invariant_field()

        equation = sp.Eq(self.symbolI, Iphi)
        result = list(sp.solve(equation, self.symbolI, **solve_kwargs))  # type: ignore

        if simplify:
            result = [sp.simplify(x, inverse=True) for x in result]

        # Sort such that solutions which have imaginary in will be last
        result.sort(key=lambda x: x.has(sp.I))

        return result

    def solve_Nfold(self, end_value, simplify=False, params={}):
        """
        Tries to solve N-fold integral.

        Parameters
        ----------
        end_value : sp.Expr, float, int
            Scalar field value at the end of inflation/
        simplify : bool, optional
            simplify result, by default False
        params : dict, optional
            Dictionary of symbol-value pairs, by default {}

        Returns
        -------
        sp.Expr
            returns N-fold function N(scalar_field)
        """

        try:
            assert isinstance(self.I_V, InflationFunction)
        except:
            raise TypeError("Function I_V not defined or wrong type.")
        integrand = 1 / self.mp**2 * self.I_V.f_s() / self.I_V.fd_s()

        free_symbols = integrand.free_symbols() - {self.symbol}
        params = {str(key): value for key, value in params.items()}

        # Substitute all parameters except A and A'
        free_variable_values = {key: params.get(str(key)) for key in list(free_symbols)}

        integrand = integrand.subs(free_variable_values)
        if isinstance(end_value, sp.Expr):
            end_value = end_value.subs(free_variable_values)

        result = sp.integrate(integrand, (self.symbolI, end_value, self.symbolI))
        if isinstance(result, sp.Integral):
            print("Couldn't solve integral analytically.")
            return result
        elif result.has(sp.I):
            print("Solution has complex number in.")
            return result
        elif result.has(sp.oo) or result.has(-sp.oo):
            print("Solution has infinity in.")
            return result

        if simplify:
            result = sp.simplify(result)

        return result

    def nsolve_Nfold_mp(self, x, y0=0, invariant=False, sign="+", solver=None, params={}, mp_kwargs={}):
        """
        Calculate N-fold function numerically using invariant potential.

        Parameters
        ----------
        x : np.ndarray or list
            Values for scalar field. x[0] is used for initial condition and x[1] is used as final point.
            x[0] should be scalar field value at the end of inflation as then we know N-fold = 0.
        y0 : int, float
            N-fold value for initial condition, by default 0 (presumed that x[0] = field value at the end of inflation)
        solver : Callable, optional
            User defined solver for differetnial equation. Takes input as (integrand, x_0, y0, x_f, *args, **kwargs) where integrand is function dy/dt and takes two inputs (t, y. Not required, by default None
        params : dict, optional
            Dictionary of symbol-value pairs. All free symbols (except scalar invariant field) must have an assigned value, by default {}

        Returns
        -------
        _type_
            Returns Callable that takes in scalar field value.
            Input can't be smaller than value used for initial condition if x[0] < x[1] and input can't be higher than value used for initial condition if x[0] > x[1].
        """
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(f"I_V function must be InflationFunction type. ({type(self.I_V)})")
        if not isinstance(x, (np.ndarray, list)):
            raise TypeError(f"x must be list or np.ndarray tpye ({type(x)}).")
        if not len(x) == 2:
            raise ValueError("x must be an array/list of length two.")

        if sign == "+":
            sign = 1
        elif sign == "-":
            sign = -1
        else:
            raise ValueError("Sign can only be + or -.")
        if invariant:
            symbol = self.symbolI
            integrand = sign * 1 / self.mp**2 * self.I_V.f_s() / self.I_V.fd_s()
        else:
            integrand = (
                sign
                * 1
                / self.mp**2
                * self.A.f_s()
                * self.V.f_s()
                * self.F.f_s()
                / (self.V.fd_s() * self.A.f_s() - 2 * self.V.f_s() * self.A.fd_s())
            )
            symbol = self.symbol

        params = _check_params([integrand], [symbol], params)

        integrand = integrand.subs(params)

        x_0 = x[0]
        x_f = x[-1]
        if x_0 == x_f:
            raise ValueError("Initial value can't equal to final value.")

        if solver is None:
            if x_0 > x_f:
                function = lambda Iphi, N: -sp.lambdify(symbol, integrand, "mpmath")(Iphi)
                N_function = mp.odefun(function, -x_0, y0, **mp_kwargs)
                N_function(-x_f)
                result = lambda z: N_function(-z)
                return result
            else:
                function = lambda Iphi, N: sp.lambdify(symbol, integrand, "mpmath")(Iphi)
                N_function = mp.odefun(function, x_0, y0, **mp_kwargs)
                N_function(x_f)
                return N_function
        else:
            function = lambda Iphi, N: sp.lambdify(symbol, integrand, "mpmath")(Iphi)
            result = solver(function, x_0, y0, x_f)
            return result

    def nsolve_Nfold_np(self, x, y0=0, invariant=False, sign="+", solver=None, params={}, sc_kwargs={}):
        """
        Calculate N-fold function numerically using invariant potential.
        Function values are assigned at all points in x. Finally interpolation is used to define N(x).

        Parameters
        ----------
        x : np.ndarray or list
            Values for scalar field. x[0] is used for initial condition and x[-1] is used as final point for differential equation. Other points between are used as evaluation points.
            x[0] should be scalar field value at the end of inflation as then we know N-fold = 0.
        y0 : int, float
            N-fold value for initial condition, by default 0 (presumed that x[0] = field value at the end of inflation)
        solver : Callable, optional
            User defined solver for differetnial equation. Takes input as (integrand, x_0, y0, x_f, *args, **kwargs) where integrand is function dy/dt and takes two inputs (t, y). Not required, by default None
        params : dict, optional
            Dictionary of symbol-value pairs. All free symbols (except scalar invariant field) must have an assigned value, by default {}

        Returns
        -------
        _type_
            Returns Callable that takes in scalar field value. This Callable is a function which is interpolation of N(x) values evaluated at points in x.
            Input must stay between x[0] and x[-1].
        """
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(f"I_V function must be InflationFunction type. ({type(self.I_V)})")
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
            raise ValueError("Sign can only be + or -.")

        if invariant:
            symbol = self.symbolI
            integrand = sign * 1 / self.mp**2 * self.I_V.f_s() / self.I_V.fd_s()
        else:
            integrand = (
                sign
                * 1
                / self.mp**2
                * self.A.f_s()
                * self.V.f_s()
                * self.F.f_s()
                / (self.V.fd_s() * self.A.f_s() - 2 * self.V.f_s() * self.A.fd_s())
            )
            symbol = self.symbol

        params = _check_params([integrand], [symbol], params)

        integrand = integrand.subs(params)

        x_0 = x[0]
        x_f = x[-1]
        if x_0 == x_f:
            raise ValueError("Initial value can't equal to final value.")

        function = lambda Iphi, N: sp.lambdify(symbol, integrand, "scipy")(Iphi)
        if solver is None:
            if sc_kwargs.get("method", None) is None:
                sc_kwargs["method"] = "LSODA"

            ode = solve_ivp(
                function, t_span=[float(x[0]), float(x[-1])], y0=[float(y0)], dense_output=True, **sc_kwargs
            )
            if ode.status == -1:
                raise RuntimeError(f"Integration step failed. (scipy ode solver)\n{ode.message}")
            elif ode.status == 1:
                raise RuntimeError(f"A termination event occurred. (scipy ode solver)\n{ode.message}")
            # N_function = interp1d(x, ode.y.reshape(-1))
            N_function = lambda y: ode.sol(y).reshape(-1)
            return N_function
        else:
            result = solver(function, x_0, y0, x_f)
            return result


class ModelCompare(BaseSolver):
    def __init__(self, model: Optional[SlowRollModel] = None):
        super().__init__(model)

        if not isinstance(self.A, InflationFunction):
            raise TypeError(f"A function must be InflationFunction type. ({type(self.A)})")
        if not isinstance(self.B, InflationFunction):
            raise TypeError(f"B function must be InflationFunction type. ({type(self.B)})")
        if not isinstance(self.V, InflationFunction):
            raise TypeError(f"V function must be InflationFunction type. ({type(self.V)})")
        if not isinstance(self.I_V, InflationFunction):
            raise TypeError(f"I_V function must be InflationFunction type. ({type(self.I_V)})")

    def compare_invariant_potential_np(self, x, invariant_scalar_field, params={}):
        if not isinstance(invariant_scalar_field, (Callable, sp.Expr)):
            raise TypeError(
                f"invariant_scalar_field must be sympy expression or callable function f(x). ({type(invariant_scalar_field)})."
            )

        functions_to_check = [self.V.f_s(), self.A.f_s(), self.I_V.f_s()]
        if isinstance(invariant_scalar_field, sp.Expr):
            functions_to_check.append(invariant_scalar_field)

        params = _check_params(
            functions_to_check,
            [self.symbol, self.symbolI],
            params,
        )

        tempA = self.A(params)
        A = lambda y: tempA.f_n(y)
        tempV = self.V(params)
        V = lambda y: tempV.f_n(y)

        if isinstance(invariant_scalar_field, sp.Expr):
            tempI_V = self.I_V.f_s().subs(self.I_V.symbol, invariant_scalar_field).subs(params)
            I_V = sp.lambdify(self.symbol, tempI_V, "scipy")
        else:
            tempI_V = self.I_V(params)
            I_V = lambda y: tempI_V.f_n(invariant_scalar_field(y))

        x = np.array(x, dtype=float)
        potential1 = V(x) / A(x) ** 2
        potential2 = I_V(x)

        return potential1, potential2

    def compare_invariant_potential_mp(self, x, invariant_scalar_field, params={}):
        if not isinstance(invariant_scalar_field, (Callable, sp.Expr)):
            raise TypeError(
                f"invariant_scalar_field must be sympy expression or callable function f(x). ({type(invariant_scalar_field)})."
            )

        if not isinstance(x, (float, Iterable, mp.mpf)):
            raise TypeError("x must be Iterable, float, int or mp.mpf type.")

        functions_to_check = [self.V.f_s(), self.A.f_s(), self.I_V.f_s()]
        if isinstance(invariant_scalar_field, sp.Expr):
            functions_to_check.append(invariant_scalar_field)

        params = _check_params(
            functions_to_check,
            [self.symbol, self.symbolI],
            params,
        )

        tempA = self.A(params)
        A = lambda y: tempA.f_n(y, mode="mpmath")
        tempV = self.V(params)
        V = lambda y: tempV.f_n(y, mode="mpmath")

        if isinstance(invariant_scalar_field, sp.Expr):
            tempI_V = self.I_V.f_s().subs(self.I_V.symbol, invariant_scalar_field).subs(params)
            I_V = sp.lambdify(self.symbol, tempI_V, "mpmath")
        else:
            tempI_V = self.I_V(params)
            I_V = lambda y: tempI_V.f_n(mp.convert(invariant_scalar_field(y)), mode="mpmath")

        if isinstance(x, Iterable):
            potential1 = [V(y) / A(y) ** 2 for y in x]
            potential2 = [I_V(y) for y in x]
        else:
            potential1 = V(x) / A(x) ** 2
            potential2 = I_V(x)

        return potential1, potential2

    def compare_invariant_potential(
        self, invariant_scalar_field, simplify=False, simplify_kwargs=dict(inverse=True), params={}
    ):
        if not isinstance(invariant_scalar_field, sp.Expr):
            raise TypeError(f"invariant_scalar_field must be sp.Expr type. ({type(invariant_scalar_field)})")

        params = _check_params(
            [self.A.f_s(), self.V.f_s(), self.I_V.f_s(), invariant_scalar_field],
            [self.symbol, self.symbolI],
            params,
            False,
        )

        A = self.A.f_s(params)
        V = self.V.f_s(params)
        I_V = self.I_V.f_s(params)

        potential1 = V / A**2
        potential2 = I_V.subs(self.symbolI, invariant_scalar_field)

        if simplify:
            potential1 = sp.simplify(potential1, **simplify_kwargs)
            potential2 = sp.simplify(potential2, **simplify_kwargs)

        return potential1, potential2

    def compare_invariant_field_der(
        self, inverse_invariant_potential, simplify=False, simplify_kwargs=dict(inverse=True), params={}
    ):
        if not isinstance(inverse_invariant_potential, sp.Expr):
            raise TypeError(f"inverse_invariant_potential must be sp.Expr type. ({type(inverse_invariant_potential)})")

        params = _check_params(
            [self.V.f_s(), self.A.f_s(), self.B.f_s(), inverse_invariant_potential],
            [self.symbol, self.IV_symbol, self.IV_symbol],
            params,
            False,
        )
        invariant_field1 = inverse_invariant_potential.subs(self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2).subs(
            params
        )
        dinvariant_field1 = sp.diff(invariant_field1, self.symbol)

        dinvariant_field2 = sp.sqrt(self.F.f_s(params))

        if simplify:
            dinvariant_field1 = sp.simplify(dinvariant_field1, **simplify_kwargs)
            dinvariant_field2 = sp.simplify(dinvariant_field2, **simplify_kwargs)

        return dinvariant_field1, dinvariant_field2

    def compare_invariant_field_der_np(self, x, inverse_invariant_potential, dx=1e-6, order=3, params={}):
        if not isinstance(inverse_invariant_potential, (Callable, sp.Expr)):
            raise TypeError(
                f"invariant_scalar_field must be sympy expression or callable function f(x). ({type(inverse_invariant_potential)})."
            )

        x = np.array(x)

        functions_to_check = [self.V.f_s(), self.A.f_s(), self.F.f_s()]
        if isinstance(inverse_invariant_potential, sp.Expr):
            functions_to_check.append(inverse_invariant_potential)
        params = _check_params(
            functions_to_check,
            [self.symbol, self.IV_symbol],
            params,
        )

        if isinstance(inverse_invariant_potential, sp.Expr):
            invariant_field_der1 = sp.lambdify(
                self.symbol,
                sp.diff(
                    (inverse_invariant_potential.subs(self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2).subs(params)),
                    self.symbol,
                ),
                "scipy",
            )(x)
        else:
            V = self.V(params)
            A = self.A(params)
            invariant_field_n = lambda y: inverse_invariant_potential(V.f_n(y) / A.f_n(y) ** 2)
            invariant_field_der1 = derivative(invariant_field_n, x, dx=dx, n=1, order=order)

        invariant_field_der2 = sp.lambdify(self.symbol, sp.sqrt(self.F.f_s()).subs(params), "scipy")(x)

        return invariant_field_der1, invariant_field_der2

    def compare_invariant_field_der_mp(self, x, inverse_invariant_potential, params={}):
        if not isinstance(inverse_invariant_potential, (Callable, sp.Expr)):
            raise TypeError(
                f"invariant_scalar_field must be sympy expression or callable function f(x). ({type(inverse_invariant_potential)})."
            )
        if not isinstance(x, (Iterable, float, int, mp.mpf)):
            raise TypeError(f"x must be some Iterable or numerical value. ({type(x)})")

        functions_to_check = [self.V.f_s(), self.A.f_s(), self.F.f_s()]
        if isinstance(inverse_invariant_potential, sp.Expr):
            functions_to_check.append(inverse_invariant_potential)
        params = _check_params(
            functions_to_check,
            [self.symbol, self.IV_symbol],
            params,
        )

        if isinstance(inverse_invariant_potential, sp.Expr):
            invariant_field_der1_f = sp.lambdify(
                self.symbol,
                sp.diff(
                    (inverse_invariant_potential.subs(self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2).subs(params)),
                    self.symbol,
                ),
                "mpmath",
            )
            if isinstance(x, Iterable):
                invariant_field_der1 = [invariant_field_der1_f(mp.convert(y)) for y in x]
            else:
                invariant_field_der1 = invariant_field_der1_f(mp.convert(x))
        else:
            V = self.V(params)
            A = self.A(params)
            invariant_field_n = lambda y: inverse_invariant_potential(
                V.f_n(y, mode="mpmath") / A.f_n(y, mode="mpmath") ** 2
            )
            if isinstance(x, Iterable):
                invariant_field_der1 = [mp.diff(invariant_field_n, mp.convert(y)) for y in x]
            else:
                invariant_field_der1 = mp.diff(invariant_field_n, mp.convert(x))

        invariant_field_der2_f = sp.lambdify(self.symbol, sp.sqrt(self.F.f_s()).subs(params), "mpmath")
        if isinstance(x, Iterable):
            invariant_field_der2 = [invariant_field_der2_f(mp.convert(y)) for y in x]
        else:
            invariant_field_der2 = invariant_field_der2_f(mp.convert(x))

        return invariant_field_der1, invariant_field_der2

    def compare_invariant_field(
        self, inverse_invariant_potential, simplify=False, simplify_kwargs=dict(inverse=True), params={}
    ):
        if not isinstance(inverse_invariant_potential, sp.Expr):
            raise TypeError(f"inverse_invariant_potential must be sp.Expr type. ({type(inverse_invariant_potential)})")

        functions_to_check = [self.V.f_s(), self.A.f_s(), self.F.f_s(), self.B.f_s()]
        if isinstance(inverse_invariant_potential, sp.Expr):
            functions_to_check.append(inverse_invariant_potential)

        params = _check_params(
            [self.V.f_s(), self.A.f_s(), self.B.f_s(), inverse_invariant_potential],
            [self.symbol, self.IV_symbol, self.IV_symbol],
            params,
            False,
        )

        invariant_field1 = inverse_invariant_potential.subs(self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2).subs(
            params
        )
        invariant_field2 = self.solve_invariant_field(params)

        if simplify:
            invariant_field1 = sp.simplify(invariant_field1, **simplify_kwargs)
            invariant_field2 = sp.simplify(invariant_field2, **simplify_kwargs)

        return invariant_field1, invariant_field2

    def compare_invariant_field_np(self, x, inverse_invariant_potential, invariant_scalar_field, params={}):
        if not isinstance(inverse_invariant_potential, (Callable, sp.Expr)):
            raise TypeError(
                f"inverse_invariant_potential must be sympy expression or callable function f(x). ({type(inverse_invariant_potential)})."
            )
        if not isinstance(invariant_scalar_field, (Callable, sp.Expr)):
            raise TypeError(
                f"invariant_scalar_field must be sympy expression or callable function f(x). ({type(invariant_scalar_field)})."
            )

        x = np.array(x)

        functions_to_check = [self.V.f_s(), self.A.f_s(), self.F.f_s()]
        if isinstance(inverse_invariant_potential, sp.Expr):
            functions_to_check.append(inverse_invariant_potential)
        if isinstance(invariant_scalar_field, sp.Expr):
            functions_to_check.append(invariant_scalar_field)

        params = _check_params(
            functions_to_check,
            [self.symbol, self.IV_symbol],
            params,
        )

        if isinstance(inverse_invariant_potential, sp.Expr):
            invariant_field1 = sp.lambdify(
                self.symbol,
                inverse_invariant_potential.subs(self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2).subs(params),
                "scipy",
            )(x)
        else:
            V = self.V(params)
            A = self.A(params)
            invariant_field1 = inverse_invariant_potential(V.f_n(x) / A.f_n(x) ** 2)

        if isinstance(invariant_scalar_field, sp.Expr):
            invariant_field2 = sp.lambdify(self.symbol, invariant_scalar_field.subs(params), "scipy")(x)
        else:
            invariant_field2 = invariant_scalar_field(x)

        return invariant_field1, invariant_field2

    def compare_invariant_field_mp(self, x, inverse_invariant_potential, invariant_scalar_field, params={}):
        if not isinstance(inverse_invariant_potential, (Callable, sp.Expr)):
            raise TypeError(
                f"inverse_invariant_potential must be sympy expression or callable function f(x). ({type(inverse_invariant_potential)})."
            )
        if not isinstance(invariant_scalar_field, (Callable, sp.Expr)):
            raise TypeError(
                f"invariant_scalar_field must be sympy expression or callable function f(x). ({type(invariant_scalar_field)})."
            )
        if not isinstance(x, (Iterable, float, int, mp.mpf)):
            raise TypeError(f"x must be some Iterable or numerical value. ({type(x)})")

        functions_to_check = [self.V.f_s(), self.A.f_s(), self.F.f_s()]
        if isinstance(inverse_invariant_potential, sp.Expr):
            functions_to_check.append(inverse_invariant_potential)
        if isinstance(invariant_scalar_field, sp.Expr):
            functions_to_check.append(invariant_scalar_field)

        params = _check_params(
            functions_to_check,
            [self.symbol, self.IV_symbol],
            params,
        )

        if isinstance(inverse_invariant_potential, sp.Expr):
            invariant_field_f = sp.lambdify(
                self.symbol,
                inverse_invariant_potential.subs(self.IV_symbol, self.V.f_s() / self.A.f_s() ** 2).subs(params),
                "mpmath",
            )
            if isinstance(x, Iterable):
                invariant_field1 = [invariant_field_f(mp.convert(y)) for y in x]
            else:
                invariant_field1 = invariant_field_f(mp.convert(x))
        else:
            V = self.V(params)
            A = self.A(params)
            invariant_field_n = lambda y: inverse_invariant_potential(
                V.f_n(y, mode="mpmath") / A.f_n(y, mode="mpmath") ** 2
            )
            if isinstance(x, Iterable):
                invariant_field1 = [invariant_field_n(mp.convert(y)) for y in x]
            else:
                invariant_field1 = invariant_field_n(mp.convert(x))

        if isinstance(invariant_scalar_field, sp.Expr):
            invariant_field2_f = sp.lambdify(self.symbol, invariant_scalar_field.subs(params), "mpmath")(x)
        else:
            invariant_field2_f = invariant_scalar_field

        if isinstance(x, Iterable):
            invariant_field2 = [invariant_field2_f(mp.convert(y)) for y in x]
        else:
            invariant_field2 = invariant_field2_f(mp.convert(x))

        return invariant_field1, invariant_field2
