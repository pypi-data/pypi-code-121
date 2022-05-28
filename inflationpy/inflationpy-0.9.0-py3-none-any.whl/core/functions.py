from abc import ABC, abstractmethod
from collections.abc import Iterable
import types
import re
from typing import Dict, List, Optional, Union
from pytest import param

import sympy as sp
import numpy as np
import mpmath as mp


class FunctionClass(ABC):
    def __init__(
        self,
        function: Union[sp.Expr, str],
        symbol: Union[str, sp.Symbol] = sp.Symbol("phi", real=True),
        mp: Union[str, sp.Symbol, int, float, sp.Rational, sp.Number] = sp.Symbol("M_p", real=True, positive=True),
        positive: bool = True,
        **kwargs,
    ):
        """_summary_

        Parameters
        ----------
        function : Union[sp.Expr, str]
            Analytical function represented with strings. Used to define function in symbolic form.
        symbol : str, optional
            Symbol to represent scalar field in analytical functions, by default "phi"
        **kwargs :
            Can incluede info about derivatives and numerical functions. Isn't meant to be used by user.
        """

        self.symbol = symbol
        self.mp = mp

        # If free parameters (all symbols except scalr field and Planck's mass) have flag postive=True
        # This might make some calculations easier
        self.positive = positive

        # Analytical functions in sympy
        self._analytical_function = function
        self._analytical_derivative = kwargs.get("_analytical_derivative", None)
        self._analytical_2_derivative = kwargs.get("_analytical_2_derivative", None)

        # Python functions to be used by numpy (converted from sympy function where module='scipy')
        self._numerical_function_np = kwargs.get("_numerical_function_np", None)
        self._numerical_derivative_np = kwargs.get("_numerical_derivative_np", None)
        self._numerical_2_derivative_np = kwargs.get("_numerical_2_derivative_np", None)

        # Python functions to be used by mpmath (converted from sympy function where module='mpmath')
        self._numerical_function_mp = kwargs.get("_numerical_function_mp", None)
        self._numerical_derivative_mp = kwargs.get("_numerical_derivative_mp", None)
        self._numerical_2_derivative_mp = kwargs.get("_numerical_2_derivative_mp", None)

        self._sorted_variables: Union[List[sp.Symbol], None] = None

    def __call__(self, parameters):
        return self.insert_parameters(parameters)

    def __repr__(self):
        return str(self._analytical_function)

    def _repr_latex_(self):
        string = f"${sp.latex(self._analytical_function)}$"
        return string

    @property
    def symbol(self):
        return self._symbol

    @property
    def mp(self):
        return self._mp

    @property
    def _analytical_function(self):
        return self.__analytical_function

    @property
    def _analytical_derivative(self):
        return self.__analytical_derivative

    @property
    def _analytical_2_derivative(self):
        return self.__analytical_2_derivative

    @property
    def _numerical_function_np(self):
        return self.__numerical_function_np

    @property
    def _numerical_derivative_np(self):
        return self.__numerical_derivative_np

    @property
    def _numerical_2_derivative_np(self):
        return self.__numerical_2_derivative_np

    @property
    def _numerical_function_mp(self):
        return self.__numerical_function_mp

    @property
    def _numerical_derivative_mp(self):
        return self.__numerical_derivative_mp

    @property
    def _numerical_2_derivative_mp(self):
        return self.__numerical_2_derivative_mp

    @symbol.setter
    def symbol(self, symbol):
        """Set symbol for scalar field.

        Parameters
        ----------
        symbol : sp.Symbol, str
            Inserted symbol for scalar field. If string, then use sympy to convert to sp.Symbol.
            Otherwise use same symbol. Always sets notion in sympy that symbol is real.
        Raises
        ------
        TypeError
            _description_
        """
        if hasattr(self, "_symbol"):
            raise RuntimeError("Can't change scalar field symbol.")
        else:
            if isinstance(symbol, sp.Symbol):
                self._symbol = sp.Symbol(str(symbol), real=True)
            elif isinstance(symbol, str):
                self._symbol = sp.Symbol(symbol, real=True)
            else:
                raise TypeError("Symbol must be string or sp.Symbol type")

    @mp.setter
    def mp(self, mp):
        """Set Planck's mass symbol for theory.

        Parameters
        ----------
        symbol : sp.Symbol, str
            Inserted symbol for Planck's mass. If string, then use sympy to convert to sp.Symbol.
            Otherwise use same symbol. Always sets notion in sympy that symbol is real.
        Raises
        ------
        TypeError
            _description_
        """
        if hasattr(self, "_mp"):
            self.insert_parameters({self.mp: mp})
        else:
            if isinstance(mp, (int, float, sp.Rational, sp.Number)):
                self._mp = sp.Number(mp)
            elif isinstance(mp, sp.Symbol):
                self._mp = sp.Symbol(str(mp), real=True, positive=True)
            elif isinstance(mp, str):
                if self._is_string_a_number(mp):
                    self._mp = sp.Number(mp)
                else:
                    self._mp = sp.Symbol(mp, real=True, positive=True)
            else:
                raise TypeError("Planck mass symbol must be string, sp.Symbol or numerical type")

    @_analytical_function.setter
    def _analytical_function(self, function):
        if "_numerical_function" in self.__dict__:
            raise ValueError("Can't add analytical function if numerical already exists.")
        elif isinstance(function, sp.Expr):  # If sympy function
            for variable in function.free_symbols:
                if str(variable) == str(self.symbol):
                    function = function.subs(variable, self.symbol)
                else:
                    function = function.subs(variable, sp.Symbol(str(variable), real=True, positive=self.positive))
            self.__analytical_function = function
        elif isinstance(function, str):
            try:
                self.__analytical_function = self._convert_string_to_function(function)
            except Exception as e:
                raise RuntimeError("Problem with converting string to sympy function\n{}".format(e))
        else:
            raise ValueError("Invalid type for analytical function.")

    @_analytical_derivative.setter
    def _analytical_derivative(self, function):
        if isinstance(function, sp.Expr):
            self.__analytical_derivative = function
        elif function is None:
            self.__analytical_derivative = None
        # elif isinstance(self._analytical_function, sp.Expr):
        #     self.__analytical_derivative = sp.diff(self._analytical_function, self.symbol)
        else:
            raise TypeError("_analytical_function isn't sympy type. Some bug.")

    @_analytical_2_derivative.setter
    def _analytical_2_derivative(self, function):
        if isinstance(function, sp.Expr):
            self.__analytical_2_derivative = function
        elif function is None:
            self.__analytical_2_derivative = None
        # elif isinstance(self._analytical_function, sp.Expr):
        #     self.__analytical_2_derivative = sp.diff(self._analytical_function, self.symbol, 2)
        else:
            raise TypeError("_analytical_function isn't sympy type. Some bug.")

    @_numerical_function_np.setter
    def _numerical_function_np(self, function):
        if function is None:
            variables = self._return_ordered_symbols()
            self.__numerical_function_np = sp.lambdify(variables, self._analytical_function, "scipy")
        elif isinstance(function, types.FunctionType):
            self.__numerical_function_np = function
        else:
            TypeError(f"New function type isn't correct ({type(function)})")

    @_numerical_derivative_np.setter
    def _numerical_derivative_np(self, function):
        if function is None:
            self.__numerical_derivative_np = None
            # variables = self._return_ordered_symbols()
            # self.__numerical_derivative_np = sp.lambdify(variables, self._analytical_derivative, "scipy")
        elif isinstance(function, types.FunctionType):
            self.__numerical_derivative_np = function
        else:
            TypeError("Numerical numpy derivative type isn't Functiontype")

    @_numerical_2_derivative_np.setter
    def _numerical_2_derivative_np(self, function):
        if function is None:
            self.__numerical_2_derivative_np = None
            # variables = self._return_ordered_symbols()
            # self.__numerical_2_derivative_np = sp.lambdify(variables, self._analytical_2_derivative, "numpy")
        elif isinstance(function, types.FunctionType):
            self.__numerical_2_derivative_np = function
        else:
            TypeError("Numerical numpy second derivative type isn't Functiontype")

    @_numerical_function_mp.setter
    def _numerical_function_mp(self, function):
        if function is None:
            variables = self._return_ordered_symbols()
            self.__numerical_function_mp = sp.lambdify(variables, self._analytical_function, "mpmath")
        elif isinstance(function, types.FunctionType):
            self.__numerical_function_mp = function
        else:
            TypeError("Numerical mpmath derivative type isn't Functiontype")

    @_numerical_derivative_mp.setter
    def _numerical_derivative_mp(self, function):
        if function is None:
            self.__numerical_derivative_mp = None
            # variables = self._return_ordered_symbols()
            # self.__numerical_derivative_mp = sp.lambdify(variables, self._analytical_derivative, "mpmath")
        elif isinstance(function, types.FunctionType):
            self.__numerical_derivative_mp = function
        else:
            TypeError("Numerical mpmath derivative type isn't Functiontype")

    @_numerical_2_derivative_mp.setter
    def _numerical_2_derivative_mp(self, function):
        if function is None:
            self.__numerical_2_derivative_mp = None
            # variables = self._return_ordered_symbols()
            # self.__numerical_2_derivative_mp = sp.lambdify(variables, self._analytical_2_derivative, "mpmath")
        elif isinstance(function, types.FunctionType):
            self.__numerical_2_derivative_mp = function
        else:
            TypeError("Numerical numpy derivative type isn't Functiontype")

    @abstractmethod
    def f_s(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None):
        """Returns analytical function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """

    @abstractmethod
    def fd_s(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None):
        """Returns analytical derivative of a function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """

    @abstractmethod
    def f2d_s(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None):
        """Returns analytical second derivative of a function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """

    @abstractmethod
    def f_n(self, x, mode: str, *args, **kwargs):
        """
        Calculate numerical values of the function in points 'x'.

        Parameters
        ----------
        mode : str
            Select which numerical package to use.

        *args:
            Values for function constant parameters.
        **kwargs:
            Dictionary of function constant parameters
        """

    @abstractmethod
    def fd_n(self, x, mode: str, *args, **kwargs):
        """
        Calculate numerical values of the function's derivative in points 'x'.

        Parameters
        ----------
        mode : str
           Select which numerical package to use.
        *args:
            Values for function constant parameters.
        **kwargs:
            Dictionary of function constant parameters
        """

    @abstractmethod
    def f2d_n(self, x, mode: str, *args, **kwargs):
        """
        Calculate numerical values of the function's second derivatve in points 'x'.

        Parameters
        ----------
        mode : str
           Select which numerical package to use.
        *args:
            Values for function constant parameters.
        **kwargs:
            Dictionary of function constant parameters
        """

    def return_variables(self):
        return list(self._numerical_function_np.__code__.co_varnames)

    def insert_parameters(self, parameters: Dict[Union[str, sp.Expr], Union[float, sp.Expr, str]]):
        """Insert parameters into the function and create new InflationFunction where inserted variables are replaced with given values.

        Parameters
        ----------
        parameters : dict
            Dictionary of inserted variables.

        Returns
        -------
        InflationFunction
            Returns same InflationFunction but only where given variables are replaced
        """
        params = dict()
        for key, value in parameters.items():
            if str(key) == str(self.symbol):
                params[self.symbol] = value
            elif str(key) == str(self.mp):
                params[self.mp] = value
            else:
                params[sp.Symbol(str(key), real=True, positive=self.positive)] = value

        # parameters = {
        #     sp.Symbol(str(key), real=True, positive=self.positive)
        #     if str(key) != str(self.symbol)
        #     else self.symbol: value
        #     for key, value in parameters.items()
        # }

        if isinstance(self.symbol, sp.Symbol):
            scalar_symbol = params.get(self.symbol, self.symbol)
            if isinstance(scalar_symbol, str):
                if self.is_string_number(scalar_symbol):
                    raise ValueError("Symbol can't be a number.")
                elif re.search("[a-zA-Z]", scalar_symbol):
                    scalar_symbol = sp.Symbol(scalar_symbol, real=True)
                    params[self.symbol] = scalar_symbol
            elif isinstance(scalar_symbol, sp.Symbol):
                pass
            elif isinstance(scalar_symbol, sp.Expr):
                raise TypeError("Scalar field symbol must be a symbol not an expression.")
            else:
                raise TypeError("Inserted scalar field must be str or sp.Symbol type.")
        else:
            scalar_symbol = self.symbol

        if isinstance(self.mp, sp.Symbol):
            plancks_constant = params.get(self.mp, self.mp)
            if isinstance(plancks_constant, str):
                if re.search("[a-zA-Z]", plancks_constant):
                    plancks_constant = sp.Symbol(plancks_constant, real=True, positive=True)
                    params[self.mp] = plancks_constant
        else:
            plancks_constant = self.mp

        new_function = self._analytical_function.subs(params)
        old_function = self._analytical_function
        while new_function != old_function:
            old_function = new_function
            new_function = new_function.subs(params)
        result = InflationFunction(new_function, symbol=scalar_symbol, mp=plancks_constant, positive=self.positive)
        return result

    def free_symbols(self):
        return self._analytical_function.free_symbols

    def dps(self, dps):
        if not isinstance(dps, int):
            raise TypeError("dps must be an integer.")
        mp.mp.dps = dps

    def simplify(self, derivative=0, **kwargs):
        if derivative == 0:
            self.__analytical_function = self._analytical_function.simplify(**kwargs)
            variables = self._return_ordered_symbols()
            self.__numerical_function_np = sp.lambdify(variables, self._analytical_function, "scipy")
            self.__numerical_function_mp = sp.lambdify(variables, self._analytical_function, "mpmath")
        elif derivative == 1:
            if self.__analytical_derivative:
                self.__analytical_derivative = self._analytical_derivative.simplify(**kwargs)
                variables = self._return_ordered_symbols()
                self.__numerical_derivative_np = sp.lambdify(variables, self._analytical_derivative, "scipy")
                self.__numerical_derivative_mp = sp.lambdify(variables, self._analytical_derivative, "mpmath")
        elif derivative == 2:
            if self.__analytical_2_derivative:
                self.__analytical_2_derivative = self._analytical_2_derivative.simplify(**kwargs)
                variables = self._return_ordered_symbols()
                self.__numerical_2_derivative_np = sp.lambdify(variables, self._analytical_2_derivative, "scipy")
                self.__numerical_2_derivative_mp = sp.lambdify(variables, self._analytical_2_derivative, "mpmath")
        elif derivative == -1:
            self.__analytical_function = self._analytical_function.simplify(**kwargs)
            if self.__analytical_derivative:
                self.__analytical_derivative = sp.diff(self._analytical_function, self.symbol).simplify(**kwargs)
            if self.__analytical_2_derivative:
                self.__analytical_2_derivative = sp.diff(self._analytical_function, self.symbol, 2).simplify(**kwargs)
            variables = self._return_ordered_symbols()
            self.__numerical_function_np = sp.lambdify(variables, self._analytical_function, "scipy")
            self.__numerical_function_mp = sp.lambdify(variables, self._analytical_function, "mpmath")
            if self.__analytical_derivative:
                self.__numerical_derivative_np = sp.lambdify(variables, self._analytical_derivative, "scipy")
                self.__numerical_derivative_mp = sp.lambdify(variables, self._analytical_derivative, "mpmath")
            if self.__analytical_2_derivative:
                self.__numerical_2_derivative_np = sp.lambdify(variables, self._analytical_2_derivative, "scipy")
                self.__numerical_2_derivative_mp = sp.lambdify(variables, self._analytical_2_derivative, "mpmath")

    @staticmethod
    def is_string_number(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def _convert_string_to_function(self, string: str) -> sp.Expr:
        """
        Converts string into sympy expression. Also sets flags real as True for each variable.
        """
        result: sp.Expr = sp.sympify(string)  # type: ignore
        for variable in result.free_symbols:
            if str(variable) == str(self.symbol):
                result = result.subs(variable, self.symbol)
            else:
                result = result.subs(variable, sp.Symbol(str(variable), real=True, positive=self.positive))

        return result

    def _return_ordered_symbols(self) -> List[sp.Symbol]:
        if "_sorted_variables" in self.__dict__ and self.__dict__["_sorted_variables"] is not None:
            return self._sorted_variables  # type: ignore
        else:
            symbols = list(self._analytical_function.free_symbols - {self.symbol})
            symbols.sort(key=lambda x: str(x).lower())
            if self.mp in symbols:
                # Take from current index and put it as first
                symbols.insert(0, symbols.pop(symbols.index(self.mp)))
            result = [self.symbol, *symbols]
            self._sorted_variables = result
            return result

    def _insert_parameters(self, parameters: Dict[Union[sp.Expr, sp.Symbol], Union[float, sp.Expr, str, sp.Symbol]]):
        """Insert parameters into the function and create new InflationFunction where inserted variables are replaced with given values.
            Same as function insert_parameters but used in program when the conversion has already been done and parameter's dictionary
            values are already in correct format.

        Parameters
        ----------
        parameters : dict
            Dictionary of inserted variables.

        Returns
        -------
        InflationFunction
            Returns same InflationFunction but only where given variables are replaced
        """
        # Replace until no changes are made

        for elem in parameters:
            if str(elem) == str(self.symbol):
                raise ValueError("Can't change scalar field symbol.")

        if isinstance(self.mp, sp.Symbol):
            plancks_constant = parameters[self.mp] if self.mp in parameters.keys() else self.mp
            if isinstance(plancks_constant, str):
                if re.search("[a-zA-Z]", plancks_constant):
                    plancks_constant = sp.Symbol(plancks_constant, real=True, positive=True)
                    parameters[self.mp] = plancks_constant
        else:
            plancks_constant = self.mp

        new_function = self._analytical_function.subs(parameters)
        old_function = self._analytical_function
        while new_function != old_function:
            old_function = new_function
            new_function = new_function.subs(parameters)
        result = InflationFunction(new_function, symbol=self.symbol, mp=plancks_constant, positive=self.positive)
        return result

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


class InflationFunction(FunctionClass):
    def __init__(
        self,
        function: Union[sp.Expr, str],
        symbol: Union[str, sp.Symbol] = sp.Symbol("phi", real=True),
        mp: Union[str, sp.Symbol, int, float, sp.Rational, sp.Number] = sp.Symbol("M_p", real=True, positive=True),
        positive: bool = True,
        **kwargs,
    ):
        super().__init__(function=function, symbol=symbol, mp=mp, positive=positive, **kwargs)

    def __add__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    self._analytical_function + other_function, symbol=self.symbol, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        self._analytical_function + other_function._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"Both function scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("All terms must be InflationFunction, int or float type.")

    def __sub__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    self._analytical_function - other_function, symbol=self.symbol, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        self._analytical_function - other_function._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"All factors' scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("All terms must be InflationFunction, int or float type.")

    def __mul__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    self._analytical_function * other_function, symbol=self.symbol, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        self._analytical_function * other_function._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"All factors' scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("All factors must be InflationFunction, int or float type.")

    def __truediv__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    self._analytical_function / other_function, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        self._analytical_function / other_function._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"Numerator and denominator scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("Numerator and denominator must be InflationFunction, int or float type.")

    def __pow__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(self._analytical_function**other_function, symbol=self.symbol, mp=self.mp, positive=self.positive)  # type: ignore
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        self._analytical_function**other_function._analytical_function,  # type: ignore
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"Base and exponent scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("Base and exponent must be InflationFunction, int or float type.")

    def __radd__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    self._analytical_function + other_function, symbol=self.symbol, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        self._analytical_function + other_function._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"Both function scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("All terms must be InflationFunction, int or float type.")

    def __rsub__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    other_function - self._analytical_function, symbol=self.symbol, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        other_function._analytical_function - self._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"All factors' scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("All terms must be InflationFunction, int or float type.")

    def __rmul__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    other_function * self._analytical_function, symbol=self.symbol, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        other_function._analytical_function * self._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"All factors' scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("All factors must be InflationFunction, int or float type.")

    def __rtruediv__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(
                    other_function / self._analytical_function, symbol=self.symbol, mp=self.mp, positive=self.positive
                )
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        other_function._analytical_function / self._analytical_function,
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"Numerator and denominator scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("Numerator and denominator must be InflationFunction, int or float type.")

    def __rpow__(self, other_function):
        if isinstance(other_function, (InflationFunction, int, float, sp.Expr)):
            if isinstance(other_function, (int, float, sp.Expr)):
                return InflationFunction(other_function**self._analytical_function, symbol=self.symbol, mp=self.mp, positive=self.positive)  # type: ignore
            else:
                if self.symbol == other_function.symbol and self.mp == other_function.mp:
                    return InflationFunction(
                        other_function._analytical_function**self._analytical_function,  # type: ignore
                        symbol=self.symbol,
                        mp=self.mp,
                        positive=self.positive,
                    )
                elif self.mp != other_function.mp:
                    raise ValueError(
                        f"Both function Planck's mass symbols must be the same. ({self.mp, other_function.mp})"
                    )
                else:
                    raise ValueError(
                        f"Base and exponent scalar field symbols must be the same. ({self.symbol, other_function.symbol})"
                    )
        else:
            raise TypeError("Base and exponent must be InflationFunction, int or float type.")

    def f(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None):
        """Returns analytical function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """
        if parameters is None:
            parameters = {}
        else:
            variables = self._analytical_function.free_symbols
            variable_dict = {str(variable): variable for variable in variables}
            params = {str(x): value for x, value in parameters.items() if str(x) in variable_dict.keys()}
            parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}

        if parameters is None:
            parameters = {}
        return InflationFunction(
            function=self._analytical_function.subs(parameters),
            symbol=self.symbol,
            mp=self.mp,
            positive=self.positive,
            **{
                "_analytical_derivative": self._analytical_derivative.subs(parameters),
                "_analytical_2_derivative": self._analytical_2_derivative.subs(parameters),
            },
        )

    def fd(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None):
        """Returns analytical derivative of a function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """
        if parameters is None:
            parameters = {}
        else:
            variables = self._analytical_derivative.free_symbols
            variable_dict = {str(variable): variable for variable in variables}
            params = {str(x): value for x, value in parameters.items() if str(x) in variable_dict.keys()}
            parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}

        return InflationFunction(function=self._analytical_derivative.subs(parameters), symbol=self.symbol, mp=self.mp, positive=self.positive)  # type: ignore

    def f2d(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None):
        """Returns analytical second derivative of a function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """
        if parameters is None:
            parameters = {}
        else:
            variables = self._analytical_2_derivative.free_symbols
            variable_dict = {str(variable): variable for variable in variables}
            params = {str(x): value for x, value in parameters.items() if str(x) in variable_dict.keys()}
            parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}

        return InflationFunction(function=self._analytical_2_derivative.subs(parameters), symbol=self.symbol, mp=self.mp, positive=self.positive)  # type: ignore

    def f_n(self, x, *args, mode: str = "scipy", **kwargs):
        """
        Calculate numerical values of the function in points 'x'.
        If mode is scipy/numpy then numpy arrays can be used for calculation. If mode is mpmath then arrays are not supported.


        Parameters
        ----------
        x : int, float, np.ndarray, mp.mpf
            Function will be evaluated in the position of "x".
        mode : str, optional
            Select which numerical package to use. Possible values are "numpy"/"scipy" or "mpmath", by default "scipy"
        *args:
            Values for function constant parameters.
        **kwargs:
            Dictionary of function constant parameters
        Returns
        -------
        int, float, np.ndarray, (mp.mpf)
            Return numerical value(s) of the function evaluated in the point(s) "x". If mode is mpmath then type can be mp.mpf as well.
        """
        if mode in ["scipy", "numpy"]:
            kwargs = {
                key: value
                for key, value in kwargs.items()
                if key in self._numerical_function_np.__code__.co_varnames[1:]
            }
        elif mode == "mpmath":
            kwargs = {
                key: value
                for key, value in kwargs.items()
                if key in self._numerical_function_mp.__code__.co_varnames[1:]
            }

        if mode in ["scipy", "numpy"]:
            result = self._numerical_function_np(np.array(x), *args, **kwargs)
            if isinstance(x, np.ndarray) and isinstance(result, (int, float)):
                result = np.full(x.shape, result)
            return result.astype(float)
        elif mode == "mpmath":
            if isinstance(x, Iterable):
                return [self._numerical_function_mp(mp.convert(y), *args, **kwargs) for y in x]
            else:
                return self._numerical_function_mp(mp.convert(x), *args, **kwargs)
        else:
            raise ValueError("Mode can be 'scipy' or 'mpmath'.")

    def fd_n(self, x, *args, mode: str = "scipy", **kwargs):
        # If numerical derivative function is not defined then let program define this function
        if self._numerical_derivative_np is None:
            self.fd_s()

        if mode in ["scipy", "numpy"]:
            kwargs = {
                key: value
                for key, value in kwargs.items()
                if key in self._numerical_derivative_np.__code__.co_varnames[1:]
            }
        elif mode == "mpmath":
            kwargs = {
                key: value
                for key, value in kwargs.items()
                if key in self._numerical_derivative_mp.__code__.co_varnames[1:]
            }

        if mode in ["scipy", "numpy"]:
            result = self._numerical_derivative_np(np.array(x), *args, **kwargs)
            if isinstance(x, np.ndarray) and isinstance(result, (int, float)):
                result = np.full(x.shape, result)
            return result.astype(float)
        elif mode == "mpmath":
            if isinstance(x, Iterable):
                return [self._numerical_derivative_mp(mp.convert(y), *args, **kwargs) for y in x]
            else:
                return self._numerical_derivative_mp(mp.convert(x), *args, **kwargs)
        else:
            raise ValueError("Mode can be 'scipy' or 'mpmath'.")

    def f2d_n(self, x, *args, mode: str = "scipy", **kwargs):
        # If numerical derivative function is not defined then let program define this function
        if self._numerical_2_derivative_np is None:
            self.f2d_s()

        if mode in ["scipy", "numpy"]:
            kwargs = {
                key: value
                for key, value in kwargs.items()
                if key in self._numerical_2_derivative_np.__code__.co_varnames[1:]
            }
        elif mode == "mpmath":
            kwargs = {
                key: value
                for key, value in kwargs.items()
                if key in self._numerical_2_derivative_mp.__code__.co_varnames[1:]
            }

        if mode in ["scipy", "numpy"]:
            result = self._numerical_2_derivative_np(np.array(x), *args, **kwargs)
            if isinstance(x, np.ndarray) and isinstance(result, (int, float)):
                result = np.full(x.shape, result)
            return result.astype(float)
        elif mode == "mpmath":
            if isinstance(x, Iterable):
                return [self._numerical_2_derivative_mp(mp.convert(y), *args, **kwargs) for y in x]
            else:
                return self._numerical_2_derivative_mp(mp.convert(x), *args, **kwargs)
        else:
            raise ValueError("Mode can be 'scipy' or 'mpmath'.")

    def f_s(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None) -> sp.Expr:
        """Returns analytical sympy function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """
        if parameters is None:
            parameters = {}
        else:
            variables = self._analytical_function.free_symbols
            variable_dict = {str(variable): variable for variable in variables}
            params = {str(x): value for x, value in parameters.items() if str(x) in variable_dict.keys()}
            parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}

        return self._analytical_function.subs(parameters)

    def fd_s(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None) -> sp.Expr:
        """Returns analytical sympy derivative of a function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """
        if self._analytical_derivative is None:
            variables = self._return_ordered_symbols()
            self._analytical_derivative = sp.diff(self._analytical_function, self.symbol)
            self._numerical_derivative_np = sp.lambdify(variables, self._analytical_derivative, "scipy")
            self._numerical_derivative_mp = sp.lambdify(variables, self._analytical_derivative, "mpmath")

        if parameters is None:
            parameters = {}
        else:
            variables = self._analytical_derivative.free_symbols
            variable_dict = {str(variable): variable for variable in variables}
            params = {str(x): value for x, value in parameters.items() if str(x) in variable_dict.keys()}
            parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}
        return self._analytical_derivative.subs(parameters)  # type: ignore

    def f2d_s(self, parameters: Optional[Dict[Union[sp.Expr, str], Union[float, str]]] = None) -> sp.Expr:
        """Returns analytical sympy second derivative of a function. If parameters dictionary is defined then substitute inserted symbols with given values.

        Parameters
        ----------
        parameters : Optional[Dict[Union[sp.Expr, str], Union[float, str]]], optional
            Dictionary to substitute symbols in analytical function, by default None
        """

        if self._analytical_2_derivative is None:
            variables = self._return_ordered_symbols()
            self._analytical_2_derivative = sp.diff(self._analytical_function, self.symbol, 2)
            self._numerical_2_derivative_np = sp.lambdify(variables, self._analytical_2_derivative, "scipy")
            self._numerical_2_derivative_mp = sp.lambdify(variables, self._analytical_2_derivative, "mpmath")

        if parameters is None:
            parameters = {}
        else:
            variables = self._analytical_2_derivative.free_symbols
            variable_dict = {str(variable): variable for variable in variables}
            params = {str(x): value for x, value in parameters.items() if str(x) in variable_dict.keys()}
            parameters = {variable_dict.get(symbol): value for symbol, value in params.items()}
        return self._analytical_2_derivative.subs(parameters)  # type: ignore

    def solve(self, *symbols, **flags):
        return sp.solve(self._analytical_function, *symbols, **flags)

    def integrate(self, *args, meijerg=None, conds="piecewise", risch=None, heurisch=None, manual=None, **kwargs):
        return sp.integrate(
            *args, meijerg=meijerg, conds=conds, risch=risch, heurisch=heurisch, manual=manual, **kwargs
        )

    def diff(self, symbol, n):
        symbol = sp.Symbol(str(symbol), real=True, positive=self.positive)
        return InflationFunction(
            sp.diff(self.f_s(), symbol, n), symbol=self.symbol, mp=self.mp, positive=self.positive
        )


def log(function: InflationFunction):
    return InflationFunction(
        function=sp.log(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def exp(function: InflationFunction):
    return InflationFunction(
        function=sp.exp(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def sin(function: InflationFunction):
    return InflationFunction(
        function=sp.sin(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def cos(function: InflationFunction):
    return InflationFunction(
        function=sp.cos(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def tan(function: InflationFunction):
    return InflationFunction(
        function=sp.tan(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def cot(function: InflationFunction):
    return InflationFunction(
        function=sp.cot(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def sec(function: InflationFunction):
    return InflationFunction(
        function=sp.sec(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def csc(function: InflationFunction):
    return InflationFunction(
        function=sp.csc(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def sinc(function: InflationFunction):
    return InflationFunction(
        function=sp.sinc(function.f_s()), symbol=function.symbol, mp=function.mp, positive=function.positive
    )


def LambertW(function: InflationFunction, k=0):
    return InflationFunction(
        function=sp.LambertW(function.f_s(), k=k), symbol=function.symbol, mp=function.mp, positive=function.positive
    )
