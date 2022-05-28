from typing import Dict, Iterable, List, Optional, Union
import re

import numpy as np
import sympy as sp
from sympy.calculus.util import continuous_domain
from sympy.solvers.inequalities import solve_univariate_inequality
import mpmath as mp

from IPython.display import display, Math

from inflationpy.core.functions import InflationFunction


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


class SlowRollModel:
    def __init__(
        self,
        A: Union[InflationFunction, sp.Expr, str, None] = None,
        B: Union[InflationFunction, sp.Expr, str, None] = None,
        V: Union[InflationFunction, sp.Expr, str, None] = None,
        I_V: Union[InflationFunction, sp.Expr, str, None] = None,
        symbol: Union[str, sp.Symbol] = sp.Symbol("phi", real=True),
        symbolI: Union[str, sp.Symbol] = sp.Symbol("I_phi", real=True),
        mp: Union[str, sp.Symbol, int, float, sp.Rational, sp.Number] = sp.Symbol("M_p", real=True, positive=True),
        palatini: bool = False,
        positive: bool = True,
    ) -> None:
        """Initialize Slow-roll model. Two possible methods (can be used at the same time).
            1) Define A, B, V functions.
            2) Define invariant potential I_V.

        Parameters
        ----------
        A : Union[InflationFunction, sp.Expr, str, None], optional
            A function, by default None
        B : Union[InflationFunction, sp.Expr, str, None], optional
            B function, by default None
        V : Union[InflationFunction, sp.Expr, str, None], optional
            V function, by default None
        I_V : Union[InflationFunction, sp.Expr, str, None], optional
            Invariant potential, by default None
        symbol : Union[str, sp.Symbol], optional
            scalar field symbol, by default sp.Symbol("phi", real=True)
        symbolI : Union[str, sp.Symbol], optional
            invariant scalar field symbol, by default sp.Symbol("I_phi", real=True)
        mp : Union[str, sp.Symbol, int, float, sp.Rational, sp.Number], optional
            Planck's mass, by default sp.Symbol("M_p", real=True)
        palatini : bool, optional
            Boolean for using palatini formalism. If false then metric formalism, by default False.
        positive : bool, optional
            Assumption for variables (not (invariant) scalar field and Planck's mass) if they behave as positive numbers.
            This is often useful for simplifications and analytical calculations, by default True
        """
        self.symbol = sp.Symbol(str(symbol), real=True)
        self.symbolI = sp.Symbol(str(symbolI), real=True)

        self.A_sym = sp.Symbol("A", real=True, positive=True)
        self.B_sym = sp.Symbol("B", real=True)
        self.V_sym = sp.Symbol("V", real=True)
        self.I_V_sym = sp.Symbol("I_V", real=True)
        self.N_sym = sp.Symbol("N", real=True, positive=True)

        self.mp = mp  # type: ignore
        self.positive = positive
        if A is None:
            self.A = None
        elif isinstance(A, InflationFunction):
            if symbol != A.symbol:
                raise ValueError("Inserted scalar field symbol for model and A function are different.")
            if positive != A.positive:
                raise ValueError("Inserted positive assumption is different than A function's.")
            self.A = InflationFunction(A.f_s(), symbol=A.symbol, mp=A.mp, positive=A.positive)
        else:
            if isinstance(A, (int, float)):
                A = str(A)
            self.A = InflationFunction(A, symbol=symbol, mp=mp, positive=self.positive)

        if B is None:
            self.B = None
        elif isinstance(B, InflationFunction):
            if symbol != B.symbol:
                raise ValueError("Inserted scalar field symbol for model and B function are different.")
            if positive != B.positive:
                raise ValueError("Inserted positive assumption is different than B function's.")
            self.B = InflationFunction(B.f_s(), symbol=B.symbol, mp=B.mp, positive=B.positive)
        else:
            if isinstance(B, (int, float)):
                B = str(B)
            self.B = InflationFunction(B, symbol=symbol, mp=mp, positive=self.positive)

        if V is None:
            self.V = None
        elif isinstance(V, InflationFunction):
            if symbol != V.symbol:
                raise ValueError("Inserted scalar field symbol for model and V function are different.")
            if positive != V.positive:
                raise ValueError("Inserted positive assumption is different than V function's.")
            self.V = InflationFunction(V.f_s(), symbol=V.symbol, mp=V.mp, positive=V.positive)
        else:
            if isinstance(V, (int, float)):
                V = str(V)
            self.V = InflationFunction(V, symbol=symbol, mp=mp, positive=self.positive)

        if I_V is None:
            self.I_V = None
        elif isinstance(I_V, InflationFunction):
            if symbolI != I_V.symbol:
                raise ValueError(
                    "Inserted invariant scalar field symbol for model and invariant potential are different."
                )
            if positive != I_V.positive:
                raise ValueError("Inserted positive assumption is different than invariant potential's")
            self.I_V = InflationFunction(I_V.f_s(), symbol=I_V.symbol, mp=I_V.mp, positive=I_V.positive)
        else:
            if isinstance(I_V, (int, float)):
                I_V = str(I_V)
            self.I_V = InflationFunction(I_V, symbol=symbolI, mp=mp, positive=self.positive)

        # Check if functions are compatible
        scalar_symbols = [x.symbol for x in [self.A, self.B, self.V] if isinstance(x, InflationFunction)]
        if len(scalar_symbols) > 1:
            if not all([scalar_symbols[0] == scalar_symbol for scalar_symbol in scalar_symbols]):
                raise ValueError("Symbol for scalar field for A, B and V functions are not same.")

        self._check_inflationfunction_compatibility()

        self.palatini = palatini
        self._init_functions()

    def __repr__(self) -> str:
        return f"A= {self.A}\nB= {self.B}\nV= {self.V}\nI_V= {self.I_V}"

    def __call__(self, parameters):
        return self.insert_parameters(parameters)

    def _repr_latex_(self):
        function_strings = [
            sp.latex(function.f_s()) if isinstance(function, InflationFunction) else "-"
            for function in [self.A, self.B, self.V, self.I_V]
        ]
        string = f"$A= {function_strings[0]} \\\\ B= {function_strings[1]} \\\\ V= {function_strings[2]} \\\\ I_V= {function_strings[3]}$"
        return string

    @property
    def palatini(self):
        return self._palatini

    @palatini.setter
    def palatini(self, is_palatini: bool):
        if hasattr(self, "_palatini"):
            if isinstance(is_palatini, bool) and self._palatini != is_palatini:
                self._palatini = is_palatini
                self._init_functions()
            elif not isinstance(is_palatini, bool):
                raise TypeError("palatini value can only be True or False.")
        else:
            if isinstance(is_palatini, bool):
                self._palatini = is_palatini
            else:
                raise TypeError("palatini value can only be True or False.")

    @staticmethod
    def is_string_number(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    @property
    def mp(self):
        return self._mp

    @mp.setter
    def mp(self, new_mp: Union[str, sp.Symbol, float, int]):

        if isinstance(new_mp, (int, float, sp.Rational, sp.Number)):
            new_mp = sp.Number(new_mp)
        elif isinstance(new_mp, sp.Symbol):
            new_mp = sp.Symbol(str(new_mp), real=True, positive=True)
        elif isinstance(new_mp, str):
            if self._is_string_a_number(new_mp):
                new_mp = sp.Number(new_mp)
            else:
                new_mp = sp.Symbol(new_mp, real=True, positive=True)
        else:
            raise TypeError("Planck mass symbol must be string, sp.Symbol or numerical type")

        if hasattr(self, "_mp"):
            if isinstance(self.A, InflationFunction):
                self.A = self.A({self.A.mp: new_mp})
            if isinstance(self.B, InflationFunction):
                self.B = self.B({self.B.mp: new_mp})
            if isinstance(self.V, InflationFunction):
                self.V = self.V({self.V.mp: new_mp})
            if isinstance(self.I_V, InflationFunction):
                self.I_V = self.I_V({self.I_V.mp: new_mp})

            if hasattr(self, "_palatini"):
                self._init_functions()

        else:
            self._mp = new_mp

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol):
        if hasattr(self, "_symbol"):
            raise RuntimeError("Can't change scalar field symbol")
        else:
            if isinstance(new_symbol, sp.Symbol):
                self._symbol = new_symbol
            else:
                raise TypeError("Scalar field symbol must be sp.Symbol type.")

    @property
    def symbolI(self):
        return self._symbolI

    @symbolI.setter
    def symbolI(self, new_symbol):
        if hasattr(self, "_symbolI"):
            raise RuntimeError("Can't change invariant scalar field symbol")
        else:
            if isinstance(new_symbol, sp.Symbol):
                self._symbolI = new_symbol
            else:
                raise TypeError("Invariant scalar field symbol must be sp.Symbol type.")

    @staticmethod
    def _is_string_a_number(string: str):
        """
        Returns True is string is a number.

        Parameters
        ----------
        string : str
            String which is being checked

        Returns
        -------
        _type_
            _description_
        """
        try:
            float(string)
            return True
        except ValueError:
            return False

    def _check_inflationfunction_compatibility(self):
        planck_symbols = [x.mp for x in [self.A, self.B, self.V, self.I_V] if isinstance(x, InflationFunction)]
        if len(planck_symbols) > 1:
            if not all([planck_symbols[0] == planck_symbol for planck_symbol in planck_symbols]):
                raise ValueError("Planck's mass symbol for A, B, V and I_V functions are not same.")

    def _init_functions(self):
        def _replace_function(function, symbol_to_replace, value):
            assert isinstance(symbol_to_replace, list), "symbols_to_replace must be a list"
            assert isinstance(value, list), "value must be a list"
            assert len(symbol_to_replace) == len(value)
            for symbol, val in zip(symbol_to_replace, value):
                function = function.subs(symbol, val)

            return function

        """
        Define all analytical functions required for calculations:
        For scalar field define:
            F (for simplification), Ɛ (slow-roll parameter), η (slow-roll parameter), n_s (scalar spectral index), r (tensor to scalr index), As (Scalar power spectrum amplitude)
        For invariant field define:
            Ɛ (slow-roll parameter), η (slow-roll parameter), n_s (scalar spectral index), r (tensor to scalr index), As (Scalar power spectrum amplitude)
        """
        A = self.A_sym
        B = self.B_sym
        V = self.V_sym
        dA = sp.Symbol("A'", real=True)
        ddA = sp.Symbol("A''", real=True)
        dB = sp.Symbol("B'", real=True)
        dV = sp.Symbol("V'", real=True)
        ddV = sp.Symbol("V''", real=True)
        mp = self.mp
        I_V = self.I_V_sym
        dI_V = sp.Symbol("I_V'", real=True)
        ddI_V = sp.Symbol("I_V''", real=True)

        if self.palatini:
            F = B / A
            dF = (A * dB - B * dA) / A**2
        else:
            F = B / A + sp.Rational(3, 2) * mp**2 * (dA / A) ** 2
            dF = (A**2 * dB - 3 * mp**2 * dA**3 - A * dA * (B - 3 * mp**2 * ddA)) / A**3

        self.F = F
        self.epsilon = mp**2 / (2 * F) * ((dV * A - 2 * V * dA) / (A * V)) ** 2
        self.eta = (
            mp**2
            / (V * F)
            * (
                ddV
                - 4 * dV * dA / A
                - dV * dF / (2 * F)
                - 2 * V * ddA / A
                + 6 * V * (dA / A) ** 2
                + V * dA * dF / (A * F)
            )
        )
        self.n_s = 1 - 6 * self.epsilon + 2 * self.eta
        self.r = 16 * self.epsilon
        self.A_s = sp.Rational(1, 24) * V / (sp.pi**2 * mp**4 * self.epsilon)
        self.N_integrand = A * V * F / (mp**2 * (dV * A - 2 * V * dA))

        self.epsilonI = mp**2 / 2 * (dI_V / I_V) ** 2
        self.etaI = mp**2 * (ddI_V / I_V)
        self.n_sI = 1 - 6 * self.epsilonI + 2 * self.etaI
        self.rI = 16 * self.epsilonI
        self.A_sI = sp.Rational(1, 24) * I_V / (sp.pi**2 * mp**4 * self.epsilonI)
        self.N_integrandI = I_V / (dI_V * mp**2)

        if isinstance(self.A, InflationFunction):
            a_list1, a_list2 = [A, dA, ddA], [self.A.f_s(), self.A.fd_s(), self.A.f2d_s()]
            self.F = _replace_function(self.F, a_list1, a_list2)
            self.epsilon = _replace_function(self.epsilon, a_list1, a_list2)
            self.eta = _replace_function(self.eta, a_list1, a_list2)
            self.n_s = _replace_function(self.n_s, a_list1, a_list2)
            self.r = _replace_function(self.r, a_list1, a_list2)
            self.A_s = _replace_function(self.A_s, a_list1, a_list2)
            self.N_integrand = _replace_function(self.N_integrand, a_list1, a_list2)
        if isinstance(self.B, InflationFunction):
            b_list1, b_list2 = [B, dB], [self.B.f_s(), self.B.fd_s()]
            self.F = _replace_function(self.F, b_list1, b_list2)
            self.epsilon = _replace_function(self.epsilon, b_list1, b_list2)
            self.eta = _replace_function(self.eta, b_list1, b_list2)
            self.n_s = _replace_function(self.n_s, b_list1, b_list2)
            self.r = _replace_function(self.r, b_list1, b_list2)
            self.A_s = _replace_function(self.A_s, b_list1, b_list2)
            self.N_integrand = _replace_function(self.N_integrand, b_list1, b_list2)
        if isinstance(self.V, InflationFunction):
            v_list1, v_list2 = [V, dV, ddV], [self.V.f_s(), self.V.fd_s(), self.V.f2d_s()]
            self.F = _replace_function(self.F, v_list1, v_list2)
            self.epsilon = _replace_function(self.epsilon, v_list1, v_list2)
            self.eta = _replace_function(self.eta, v_list1, v_list2)
            self.n_s = _replace_function(self.n_s, v_list1, v_list2)
            self.r = _replace_function(self.r, v_list1, v_list2)
            self.A_s = _replace_function(self.A_s, v_list1, v_list2)
            self.N_integrand = _replace_function(self.N_integrand, v_list1, v_list2)

        if (
            isinstance(self.A, InflationFunction)
            and isinstance(self.B, InflationFunction)
            and isinstance(self.B, InflationFunction)
        ):
            self.F = InflationFunction(self.F.doit(), symbol=self.symbol, mp=self.mp, positive=self.positive)
            self.epsilon = InflationFunction(
                self.epsilon.doit(), symbol=self.symbol, mp=self.mp, positive=self.positive
            )
            self.eta = InflationFunction(self.eta.doit(), symbol=self.symbol, mp=self.mp, positive=self.positive)
            self.n_s = InflationFunction(self.n_s.doit(), symbol=self.symbol, mp=self.mp, positive=self.positive)
            self.r = InflationFunction(self.r.doit(), symbol=self.symbol, mp=self.mp, positive=self.positive)
            self.A_s = InflationFunction(self.A_s.doit(), symbol=self.symbol, mp=self.mp, positive=self.positive)
            self.N_integrand = InflationFunction(
                self.N_integrand.doit(), symbol=self.symbol, mp=self.mp, positive=self.positive
            )

        elif isinstance(self.A, InflationFunction) and isinstance(self.B, InflationFunction):
            self.F = InflationFunction(self.F, symbol=self.symbol, mp=self.mp, positive=self.positive)

        if isinstance(self.I_V, InflationFunction):
            iv_list1, iv_list2 = [I_V, dI_V, ddI_V], [self.I_V.f_s(), self.I_V.fd_s(), self.I_V.f2d_s()]
            self.epsilonI = InflationFunction(
                _replace_function(self.epsilonI, iv_list1, iv_list2).doit(),
                symbol=self.symbolI,
                mp=self.mp,
                positive=self.positive,
            )
            self.etaI = InflationFunction(
                _replace_function(self.etaI, iv_list1, iv_list2).doit(),
                symbol=self.symbolI,
                mp=self.mp,
                positive=self.positive,
            )
            self.n_sI = InflationFunction(
                _replace_function(self.n_sI, iv_list1, iv_list2).doit(),
                symbol=self.symbolI,
                mp=self.mp,
                positive=self.positive,
            )
            self.rI = InflationFunction(
                _replace_function(self.rI, iv_list1, iv_list2).doit(),
                symbol=self.symbolI,
                mp=self.mp,
                positive=self.positive,
            )
            self.A_sI = InflationFunction(
                _replace_function(self.A_sI, iv_list1, iv_list2).doit(),
                symbol=self.symbolI,
                mp=self.mp,
                positive=self.positive,
            )
            self.N_integrandI = InflationFunction(
                _replace_function(self.N_integrandI, iv_list1, iv_list2).doit(),
                symbol=self.symbolI,
                mp=self.mp,
                positive=self.positive,
            )

    def insert_parameters(self, parameters: dict):
        """
        Insert/replace free parameters in model (in all functions). (invariant) scalar field symbol can't be replaced with numerical value. Must be another symbol.

        Parameters
        ----------
        parameters : dict
            dictionary of (symbol - symbol value) pairs. Symbol value can be another symbol.

        Returns
        -------
        SlowRollModel with replaced parameters.
        """
        params = dict()
        for key, value in parameters.items():
            if str(key) == str(self.symbol):
                params[self.symbol] = value
            elif str(key) == str(self.mp):
                params[self.mp] = value
            else:
                params[sp.Symbol(str(key), real=True, positive=self.positive)] = value

        functions = {}

        for elem in params:
            if str(elem) == str(self.symbol):
                raise ValueError("Can't change scalar field symbol.")
            if str(elem) == str(self.symbolI):
                raise ValueError("Can't change invariant scalar field symbol.")

        if isinstance(self.mp, sp.Symbol):
            plancks_constant = params.get(self.mp, self.mp)
            if isinstance(plancks_constant, str):
                if re.search("[a-zA-Z]", plancks_constant):
                    plancks_constant = sp.Symbol(plancks_constant, real=True, positive=True)
                    params[self.mp] = plancks_constant
        else:
            plancks_constant = self.mp

        functions["A"] = self.A._insert_parameters(params) if isinstance(self.A, InflationFunction) else None  # type: ignore
        functions["B"] = self.B._insert_parameters(params) if isinstance(self.B, InflationFunction) else None  # type: ignore
        functions["V"] = self.V._insert_parameters(params) if isinstance(self.V, InflationFunction) else None  # type: ignore
        functions["I_V"] = self.I_V._insert_parameters(params) if isinstance(self.I_V, InflationFunction) else None  # type: ignore
        # Change class Planck's constant value if Planck constant in changeable paramters dictionary

        model = SlowRollModel(
            symbol=self.symbol, symbolI=self.symbolI, mp=plancks_constant, palatini=self.palatini, **functions
        )

        return model

    def calculate_ns_mp(self, scalar_value, invariant=False, params={}):
        if invariant:
            function = self.n_sI
            symbol = self.symbolI
        else:
            function = self.n_s
            symbol = self.symbol
        if isinstance(scalar_value, sp.Expr):
            params = _check_params([function.f_s(), scalar_value], [symbol], params)
            scalar_value = scalar_value.subs(params)
        else:
            params = _check_params([function.f_s()], [symbol], params)

        function = function(params)

        if isinstance(scalar_value, Iterable):
            if isinstance(scalar_value, np.ndarray):
                if scalar_value.shape == ():
                    return function.f_n(mp.convert(scalar_value.item()), mode="mpmath")
            return [function.f_n(mp.convert(x), mode="mpmath") for x in scalar_value]
        elif isinstance(scalar_value, sp.Expr):
            return function.f_n(mp.convert(sp.N(scalar_value, mp.mp.dps)), mode="mpmath")
        else:
            return function.f_n(mp.convert(scalar_value), mode="mpmath")

    def calculate_ns_np(self, scalar_value, invariant=False, params={}):
        if invariant:
            function = self.n_sI
            symbol = self.symbolI
        else:
            function = self.n_s
            symbol = self.symbol
        if isinstance(scalar_value, sp.Expr):
            params = _check_params([function.f_s(), scalar_value], [symbol], params)
            scalar_value = scalar_value.subs(params)
        else:
            params = _check_params([function.f_s()], [symbol], params)

        function = function(params)

        if isinstance(scalar_value, Iterable):
            scalar_value = np.array(scalar_value, dtype=float)
            if isinstance(scalar_value, np.ndarray):
                if scalar_value.shape == ():
                    return function.f_n(float(scalar_value.item()))
            result = function.f_n(scalar_value)
            if isinstance(scalar_value, np.ndarray) and isinstance(result, (int, float)):
                result = np.full(scalar_value.shape, result)
            return result
        elif isinstance(scalar_value, sp.Expr):
            return function.f_n(float(scalar_value), mode="numpy")
        else:
            return function.f_n(float(x), mode="numpy")

    def calculate_ns(self, scalar_value, invariant=False, params={}):
        if invariant:
            function = self.n_sI
            symbol = self.symbolI
        else:
            function = self.n_s
            symbol = self.symbol

        if isinstance(scalar_value, sp.Expr):
            free_variables = function.free_symbols().union(scalar_value.free_symbols)
        else:
            free_variables = function.free_symbols()
        variable_dict = {str(variable): variable for variable in free_variables}
        params = {str(x): value for x, value in params.items() if str(x) in variable_dict.keys()}
        params = {variable_dict.get(symbol): value for symbol, value in params.items()}

        function = function(params)

        if isinstance(scalar_value, sp.Expr):
            scalar_value = scalar_value.subs(params)

        if isinstance(scalar_value, Iterable):
            if isinstance(scalar_value, np.ndarray):
                if scalar_value.shape == ():
                    return function.f_s({symbol: scalar_value.item()})
            return [function.f_s({symbol: x}) for x in scalar_value]
        else:
            return function.f_s({symbol: scalar_value})

    def calculate_r_mp(self, scalar_value, invariant=False, params={}):
        if invariant:
            function = self.rI
            symbol = self.symbolI
        else:
            function = self.r
            symbol = self.symbol
        if isinstance(scalar_value, sp.Expr):
            params = _check_params([function.f_s(), scalar_value], [symbol], params)
            scalar_value = scalar_value.subs(params)
        else:
            params = _check_params([function.f_s()], [symbol], params)

        function = function(params)

        if isinstance(scalar_value, Iterable):
            if isinstance(scalar_value, np.ndarray):
                if scalar_value.shape == ():
                    return function.f_n(mp.convert(scalar_value.item()), mode="mpmath")
            return [function.f_n(mp.convert(x), mode="mpmath") for x in scalar_value]
        elif isinstance(scalar_value, sp.Expr):
            return function.f_n(mp.convert(sp.N(scalar_value, mp.mp.dps)), mode="mpmath")
        else:
            return function.f_n(mp.convert(scalar_value), mode="mpmath")

    def calculate_r_np(self, scalar_value, invariant=False, params={}):
        if invariant:
            function = self.rI
            symbol = self.symbolI
        else:
            function = self.r
            symbol = self.symbol
        if isinstance(scalar_value, sp.Expr):
            params = _check_params([function.f_s(), scalar_value], [symbol], params)
            scalar_value = scalar_value.subs(params)
        else:
            params = _check_params([function.f_s()], [symbol], params)

        function = function(params)

        if isinstance(scalar_value, Iterable):
            scalar_value = np.array(scalar_value, dtype=float)
            if isinstance(scalar_value, np.ndarray):
                if scalar_value.shape == ():
                    return function.f_n(float(scalar_value.item()))
            result = function.f_n(scalar_value)
            if isinstance(scalar_value, np.ndarray) and isinstance(result, (int, float)):
                result = np.full(scalar_value.shape, result)
            return result
        elif isinstance(scalar_value, sp.Expr):
            return function.f_n(float(scalar_value), mode="numpy")
        else:
            return function.f_n(float(x), mode="numpy")

    def calculate_r(self, scalar_value, invariant=False, params={}):
        if invariant:
            function = self.rI
            symbol = self.symbolI
        else:
            function = self.r
            symbol = self.symbol

        if isinstance(scalar_value, sp.Expr):
            free_variables = function.free_symbols().union(scalar_value.free_symbols)
        else:
            free_variables = function.free_symbols()
        variable_dict = {str(variable): variable for variable in free_variables}
        params = {str(x): value for x, value in params.items() if str(x) in variable_dict.keys()}
        params = {variable_dict.get(symbol): value for symbol, value in params.items()}

        function = function(params)

        if isinstance(scalar_value, sp.Expr):
            scalar_value = scalar_value.subs(params)

        if isinstance(scalar_value, Iterable):
            if isinstance(scalar_value, np.ndarray):
                if scalar_value.shape == ():
                    return function.f_s({symbol: scalar_value.item()})
            return [function.f_s({symbol: x}) for x in scalar_value]
        else:
            return function.f_s({symbol: scalar_value})

    def free_symbols(self, invariant=False):
        """Returns all free symbols/parameters of the slow-roll model.

        Parameters
        ----------
        invariant : bool, optional
            Boolean to return invariant model free symbols, by default False

        Returns
        -------
        set
            Set of free parameters.
        """
        free_syms = set()
        if invariant:
            for function in [self.I_V]:
                if isinstance(function, InflationFunction):
                    free_syms = free_syms.union(function.free_symbols())
        else:
            for function in [
                self.A,
                self.B,
                self.V,
            ]:
                if isinstance(function, InflationFunction):
                    free_syms = free_syms.union(function.free_symbols())
        return free_syms

    def normalize_potential(self, scalar_value, invariant=False, params={}):
        """
        Calculate constant value for potential from scalar field amplitude. Observational data is from Planck 2018 https://arxiv.org/abs/1807.06211.
        - Akrami, Planck Collaboration Y. et al. “Planck 2018 results. X. Constraints on inflation.” (2018).
        """
        free_symbols = set()
        if isinstance(scalar_value, sp.Expr):
            free_symbols = scalar_value.free_symbols
        if invariant:
            if not isinstance(self.I_V, InflationFunction):
                raise TypeError(f"Invariant potential must be InflationFunction type ({type(self.I_V)})")
            free_symbols = free_symbols.union(self.I_V.free_symbols()).union(self.epsilonI.free_symbols()) - {
                self.symbolI
            }
        else:
            if not isinstance(self.V, InflationFunction):
                raise TypeError(f"Potential function must be InflationFunction type ({type(self.V)})")
            if not isinstance(self.epsilon, InflationFunction):
                raise TypeError(f"Epsilon function must be InflationFunction type ({type(self.epsilon)})")
            free_symbols = free_symbols.union(self.V.free_symbols()).union(self.epsilon.free_symbols()) - {self.symbol}

        variable_dict = {str(variable): variable for variable in free_symbols}
        parameters = {str(x): value for x, value in params.items() if str(x) in variable_dict.keys()}
        params = {variable_dict.get(symbol): value for symbol, value in parameters.items()}

        if invariant:
            assert isinstance(self.I_V, InflationFunction), "Invariant potential is not InflationFunction type"
            potential = self.I_V(params).f_s()
            epsilon = self.epsilonI(params).f_s()
            symbol = self.symbolI
        else:
            assert isinstance(self.V, InflationFunction), "Potential function is not InflationFunction type"
            potential = self.V(params).f_s()
            epsilon = self.epsilon(params).f_s()
            symbol = self.symbol

        experimental_value = sp.exp(3.044)
        As = sp.Rational(1, 24) * potential / (self.mp**4 * sp.pi**2 * epsilon)
        M = sp.root(experimental_value * sp.Pow(10, -10) / As, 4).subs({symbol: scalar_value}).subs(params)

        # ln(10^10 * A_s) = 3.044 ± 0.014

        return M

    def inspect(self, domain=sp.Reals, invariant=False):
        if not isinstance(invariant, bool):
            raise TypeError("invaraint value must be boolean.")
        if invariant:
            if not isinstance(self.I_V, InflationFunction):
                raise ValueError("Invariant potential not defined.")
            try:
                if isinstance(self.I_V, InflationFunction):
                    iv_domain = continuous_domain(self.I_V.f_s(), self.symbolI, domain=domain)
                else:
                    raise TypeError()
            except:
                iv_domain = "-"
            try:
                if isinstance(self.epsilonI, InflationFunction):
                    epsilon_domain = continuous_domain(self.epsilonI.f_s(), self.symbolI, domain=domain)
                else:
                    raise TypeError()
            except:
                epsilon_domain = "-"
            try:
                if isinstance(self.etaI, InflationFunction):
                    eta_domain = continuous_domain(self.etaI.f_s(), self.symbolI, domain=domain)
                else:
                    raise TypeError()
            except:
                eta_domain = "-"

            if isinstance(iv_domain, sp.sets.fancysets.Reals):
                display(Math(f"I_V: \phi \in {sp.latex(iv_domain)}"))
            if isinstance(epsilon_domain, sp.sets.fancysets.Reals):
                display(Math(f"\epsilon: \phi \in {sp.latex(epsilon_domain)}"))
            else:
                display(Math(f"\epsilon: {sp.latex(epsilon_domain)}"))
            if isinstance(eta_domain, sp.sets.fancysets.Reals):
                display(Math(f"\eta: \phi \in {sp.latex(eta_domain)}"))
            else:
                display(Math(f"\eta: {sp.latex(eta_domain)}"))
            domain = sp.Reals
            for domain_val in [iv_domain, epsilon_domain, eta_domain]:
                domain = domain.intersect(domain_val) if domain_val != "-" else domain
            display(Math(f"\\text{{Intersection}}: {sp.latex(domain)}"))
            return iv_domain, epsilon_domain, eta_domain, domain
        else:
            try:
                if isinstance(self.A, InflationFunction):
                    a_domain = solve_univariate_inequality(
                        self.A.f_s() > 0, self.symbol, relational=False, domain=domain
                    )
                else:
                    raise TypeError()
            except:
                a_domain = "-"
            try:
                if isinstance(self.B, InflationFunction):
                    b_domain = continuous_domain(self.B.f_s(), self.symbol, domain=domain)
                else:
                    raise TypeError()
            except:
                b_domain = "-"
            try:
                if isinstance(self.V, InflationFunction):
                    v_domain = continuous_domain(self.V.f_s(), self.symbol, domain=domain)
                else:
                    raise TypeError()
            except:
                v_domain = "-"

            if self.palatini:
                try:
                    if isinstance(self.A, InflationFunction) and isinstance(self.B, InflationFunction):
                        func = 2 * self.A.f_s() * self.B.f_s()
                        f_domain = solve_univariate_inequality(func > 0, self.symbol, relational=False, domain=domain)
                    else:
                        raise TypeError()
                except:
                    f_domain = "-"
            else:
                try:
                    if isinstance(self.A, InflationFunction) and isinstance(self.B, InflationFunction):
                        func = 2 * self.A.f_s() * self.B.f_s() + 3 * self.mp * self.A.fd_s() ** 2
                        f_domain = solve_univariate_inequality(func > 0, self.symbol, relational=False, domain=domain)
                    else:
                        raise TypeError()
                except:
                    f_domain = "-"
            try:
                if isinstance(self.epsilon, InflationFunction):
                    epsilon_domain = continuous_domain(self.epsilon.f_s(), self.symbol, domain=domain)
                else:
                    raise TypeError()
            except:
                epsilon_domain = "-"
            try:
                if isinstance(self.eta, InflationFunction):
                    eta_domain = continuous_domain(self.eta.f_s(), self.symbol, domain=domain)
                else:
                    raise TypeError()
            except:
                eta_domain = "-"

            if isinstance(a_domain, sp.sets.fancysets.Reals):
                display(Math(f"A: \phi \in {sp.latex(a_domain)}"))
            else:
                display(Math(f"A: {sp.latex(a_domain)}"))
            if isinstance(b_domain, sp.sets.fancysets.Reals):
                display(Math(f"B: \phi \in {sp.latex(b_domain)}"))
            else:
                display(Math(f"B: {sp.latex(b_domain)}"))
            if isinstance(v_domain, sp.sets.fancysets.Reals):
                display(Math(f"V: \phi \in {sp.latex(v_domain)}"))
            else:
                display(Math(f"V: {sp.latex(a_domain)}"))
            if isinstance(f_domain, sp.sets.fancysets.Reals):
                display(Math(f"F: \phi \in {sp.latex(f_domain)}"))
            else:
                display(Math(f"F: {sp.latex(f_domain)}"))
            if isinstance(epsilon_domain, sp.sets.fancysets.Reals):
                display(Math(f"\epsilon: \phi \in {sp.latex(epsilon_domain)}"))
            else:
                display(Math(f"\epsilon: {sp.latex(epsilon_domain)}"))
            if isinstance(eta_domain, sp.sets.fancysets.Reals):
                display(Math(f"\eta: \phi \in {sp.latex(eta_domain)}"))
            else:
                display(Math(f"\eta: {sp.latex(eta_domain)}"))

            domain = sp.Reals
            for domain_val in [a_domain, b_domain, v_domain, f_domain, epsilon_domain, eta_domain]:
                domain = domain.intersect(domain_val) if domain_val != "-" else domain
            display(Math(f"\\text{{Intersection}}: {sp.latex(domain)}"))

            return a_domain, b_domain, v_domain, f_domain, epsilon_domain, eta_domain

    def simplify(self, derivative=0, inverse=False):
        if inverse:
            for func in [self.epsilonI, self.etaI, self.N_integrandI, self.n_sI, self.rI, self.A_sI]:
                if isinstance(func, InflationFunction):
                    func.simplify(derivative=derivative)
        else:
            for func in [self.F, self.epsilon, self.eta, self.N_integrand, self.n_s, self.r, self.A_s]:
                if isinstance(func, InflationFunction):
                    func.simplify(derivative=derivative)
