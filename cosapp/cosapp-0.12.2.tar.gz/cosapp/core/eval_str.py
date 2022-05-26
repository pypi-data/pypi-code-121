"""
Module handling the execution of code provided as string by the user.

This code is inspired from the OpenMDAO module openmdao.components.exec_comp.
"""
import re
import numpy
from numbers import Number
from typing import Any, Dict, Iterable, Optional, Tuple, Union, Callable, FrozenSet


class ContextLocals(dict):
    """Sub-set of context attributes.
    
    Parameters
    ----------
    context: System
        System whose attributes are looked up
    """

    def __init__(self, context: "System", *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.__context = context
    
    @property
    def context(self) -> "System":
        """cosapp.systems.System: Context of the locals"""
        return self.__context

    def __missing__(self, key: Any) -> Any:
        try:
            value = getattr(self.__context, key)
        except AttributeError:
            raise KeyError(key)
        else:
            self[key] = value
            return value


class EvalString:
    """Create a executable statement using an expression string.

    The following functions are available for use in expression:

    =========================  ====================================
    Function                   Description
    =========================  ====================================
    abs(x)                     Absolute value of x
    acos(x)                    Inverse cosine of x
    acosh(x)                   Inverse hyperbolic cosine of x
    arange(start, stop, step)  Array creation
    arccos(x)                  Inverse cosine of x
    arccosh(x)                 Inverse hyperbolic cosine of x
    arcsin(x)                  Inverse sine of x
    arcsinh(x)                 Inverse hyperbolic sine of x
    arctan(x)                  Inverse tangent of x
    asin(x)                    Inverse sine of x
    asinh(x)                   Inverse hyperbolic sine of x
    atan(x)                    Inverse tangent of x
    cos(x)                     Cosine of x
    cosh(x)                    Hyperbolic cosine of x
    cross(x, y)                Cross product of arrays x and y
    dot(x, y)                  Dot-product of x and y
    e                          Euler's number
    erf(x)                     Error function
    erfc(x)                    Complementary error function
    exp(x)                     Exponential function
    expm1(x)                   exp(x) - 1
    factorial(x)               Factorial of all numbers in x
    fmax(x, y)                 Element-wise maximum of x and y
    fmin(x, y)                 Element-wise minimum of x and y
    inner(x, y)                Inner product of arrays x and y
    isinf(x)                   Element-wise detection of numpy.inf
    isnan(x)                   Element-wise detection of numpy.nan
    kron(x, y)                 Kronecker product of arrays x and y
    linspace(x, y, N)          Numpy linear spaced array creation
    log(x)                     Natural logarithm of x
    log10(x)                   Base-10 logarithm of x
    log1p(x)                   log(1+x)
    matmul(x, y)               Matrix multiplication of x and y
    maximum(x, y)              Element-wise maximum of x and y
    minimum(x, y)              Element-wise minimum of x and y
    ones(N)                    Create an array of ones
    outer(x, y)                Outer product of x and y
    pi                         Pi
    power(x, y)                Element-wise x**y
    prod(x)                    The product of all elements in x
    sin(x)                     Sine of x
    sinh(x)                    Hyperbolic sine of x
    sum(x)                     The sum of all elements in x
    round(x)                   Round all elements in x
    tan(x)                     Tangent of x
    tanh(x)                    Hyperbolic tangent of x
    tensordot(x, y)            Tensor dot product of x and y
    zeros(N)                   Create an array of zeros
    =========================  ====================================

    Full list is returned by `EvalString.available_symbols()`

    Parameters
    ----------
    expression : str
        Interpretable Python statement. In addition to standard Python operators,
        a subset of numpy and scipy functions is supported.
    context : cosapp.core.module.Module or cosapp.core.numerics.basics.Residue
        System or Residue defining the local context in which the statement will be executed

    Notes
    -----
    The context is used to include the `System` ports, children, inwards and outwards.
    If the context is a `Residue`, the reference value from the residue is added as
    `residue_reference` variable in the execution context.
    """

    # this dict will act as the global scope when we eval our expressions
    __globals = {}  # type: Dict[str, Any]

    @classmethod
    def available_symbols(cls) -> Dict[str, Any]:
        """
        List of available symbols (constants and functions) in current execution context.

        Returns
        -------
        Dict[str, Any]
            Mapping of available symbols by their name.
        """
        mapping = cls.__globals

        if len(mapping) > 0:
            return mapping
        
        def add_symbols(
            module: object, names: Optional[Iterable[str]] = None
        ) -> None:
            """
            Map attribute names from the given module into the global dict.

            Parameters
            ----------
            mod : object
                Module to check.
            names : iter of str, optional
                If supplied, only map attrs that match the given names
            """
            if names is None:
                names = dir(module)
            for name in names:
                if isinstance(name, tuple):
                    name, alias = name
                else:
                    alias = name
                if not name.startswith("_"):
                    mapping[alias] = mapping[name] = getattr(module, name)

        add_symbols(numpy,
            names=[
                # Numpy types
                "int8",
                "int16",
                "int32",
                "int64",
                "uint8",
                "uint16",
                "uint32",
                "uint64",
                "float32",
                "float64",
                "complex64",
                "complex128",
                # Array functions
                "abs",
                "array",
                "asarray",
                "arange",
                "concatenate",
                "ones",
                "zeros",
                "full",
                "full_like",
                "linspace",  # Array creation
                "e",
                "pi",  # Constants
                "inf",
                "isinf",
                "isnan",  # Logic
                "log",
                "log10",
                "log1p",
                "power",
                "sqrt",  # Math operations
                "cbrt",
                "exp",
                "expm1",
                "fmax",
                "fmin",
                "maximum",
                "minimum",
                "round",
                "sum",
                "dot",
                "prod",  # Reductions
                "tensordot",
                "matmul",  # Linear algebra
                "cross",
                "outer",
                "inner",
                "kron",
                "sin",
                "cos",
                "tan",
                ("arcsin", "asin"),  # Trig
                ("arccos", "acos"),
                ("arctan", "atan"),
                "sinh",
                "cosh",
                "tanh",
                ("arcsinh", "asinh"),  # Hyperbolic trig
                ("arccosh", "acosh"),
            ],
        )
        add_symbols(numpy.linalg, names=["norm"])

        # if scipy is available, add few specials functions
        try:
            import scipy.special
        except ImportError:
            pass
        else:
            add_symbols(scipy.special,
                names=["factorial", "erf", "erfc"]
            )

        # Add residues helper function
        from cosapp.core.numerics.residues import Residue
        mapping["evaluate_residue"] = Residue.evaluate_residue
        mapping["residue_norm"] = Residue.residue_norm

        return mapping

    def __init__(self, expression: Any, context: "System") -> None:
        """Class constructor.

        Compiles an expression, and checks that it is evaluable within a given context.
        """
        from cosapp.systems import System
        if not isinstance(context, System):
            cname = type(context).__name__
            raise TypeError(
                f"Object of type {cname!r} is not a valid context to evaluate expression '{expression}'."
            )

        self.__str = EvalString.string(expression)  # type: str
        if len(self.__str) == 0:
            raise ValueError("Can't evaluate empty expressions")

        code = compile(self.__str, "<string>", "eval")  # type: CodeType

        # Look for the requested variables
        global_dict = self.available_symbols()
        self.__locals = local_dict = ContextLocals(context)  # type: ContextLocals
        value = eval(code, global_dict, local_dict)
        
        self.__vars = None  # type: FrozenSet[str]
        
        constants = context.properties
        self.__constant = set(local_dict).issubset(constants)  # type: bool

        if self.__constant:
            # simply return constant value
            eval_impl = lambda: value
        else:            
            # By specifying global and local contexts, we limit the user scope.
            eval_impl = lambda: eval(code, self.globals, self.locals)
        self.__eval = eval_impl  # type: Callable[[], Any]

    @staticmethod
    def string(expression: Any) -> str:
        """Converts an expression into a suitably formatted string.

        Notes
        -----
        Necessary step for numpy arrays (and possibly other types), whose plain string
        conversion is not readily evaluable (hence the use of 'repr' instead of 'str').

        Examples
        --------
        >>> str(numpy.array([0.1, 0.2]))
        [0.1 0.2]
        
        >>> repr(numpy.array([0.1, 0.2]))
        array([0.1, 0.2])
        """
        if isinstance(expression, str):
            # Include a substitution pass to make sure that no spaces are left
            # between objects and attributes, that is "foo.bar" instead of "foo .  bar"
            return re.sub("(?![0-9]) *\. *(?![0-9])", ".", expression.strip())
        elif isinstance(expression, EvalString):
            return str(expression)
        else:
            return repr(expression)

    def __str__(self) -> str:
        return self.__str

    def __repr__(self) -> str:
        return repr(self.__str)

    def __contains__(self, pattern: str):
        return (pattern in self.__str)

    @property
    def locals(self) -> Dict[str, Any]:
        """Dict[str, Any]: Context attributes required to evaluate the string expression."""
        # Read attribute values from context object
        eval_context = self.eval_context
        for key in self.__locals:
            self.__locals[key] = getattr(eval_context, key)
        return self.__locals

    @property
    def globals(self) -> Dict[str, Any]:
        """Dict[str, Any]: Global functions and variables required to evaluate the string expression."""
        return EvalString.__globals

    @property
    def eval_context(self) -> "System":
        """cosapp.systems.System: Context of string expression evaluation."""
        return self.__locals.context

    @property
    def constant(self) -> bool:
        """bool: `True` if evaluated expression is constant,
        that is independent of its context; `False` otherwise.
        """
        return self.__constant

    def eval(self) -> Any:
        """Evaluate the expression in the system context.

        Returns
        -------
        Any
            The result of the expression evaluation.
        """
        return self.__eval()

    def variables(self) -> FrozenSet[str]:
        """Extracts all variables required for the evaluation of the expression
        
        Returns
        -------
        FrozenSet[str]:
            Variable names as a set of strings
        """
        if self.__vars is None:
            from cosapp.systems import System
            from cosapp.ports.port import BasePort
            names = set()
            expression = str(self)
            for key, obj in self.__locals.items():
                if isinstance(obj, (System, BasePort)):
                    names |= set(f"{key}{tail}"
                        for tail in re.findall(f"{key}(\.[\w\.]*)+", expression)
                    )
                else:
                    names.add(key)
            self.__vars = frozenset(
                names - set(self.eval_context.properties)
            )
        return self.__vars


class AssignString:
    """Create an executable assignment of the kind 'lhs = rhs' from two evaluable expressions lhs and rhs."""

    def __init__(self, lhs: str, rhs: Any, context: "System") -> None:
        lhs = EvalString(lhs, context)
        if lhs.constant:
            raise ValueError(
                f"The left-hand side of an assignment expression cannot be constant ({lhs!r})")
        # At this point, lhs is a valid expression within given context
        self.__sides = None
        self.__raw_sides = [str(lhs), str(rhs)]  # raw sides lhs and rhs, without reformatting
        value = lhs.eval()
        if isinstance(value, numpy.ndarray):
            self.__shape = value.shape
            self.__dtype = value.dtype
        else:
            self.__shape = None
            self.__dtype = type(value)
        self.__context = context
        self.__lhs_vars = lhs.variables()
        self.__rhs_vars = frozenset()
        self.__locals = lhs.locals.copy()
        self.__locals.update({"rhs_value": value, context.name: context})
        assignment = f"{context.name}.{lhs!s} = rhs_value"
        self.__code = compile(assignment, "<string>", "exec")  # assignment bytecode
        self.rhs = rhs

    @property
    def eval_context(self) -> "System":
        """cosapp.systems.System: Evaluation context of the assignment."""
        return self.__context

    @property
    def lhs(self) -> str:
        """str: Left-hand side of the assignment."""
        return self.__raw_sides[0]

    @property
    def lhs_variables(self) -> FrozenSet[str]:
        """FrozenSet[str]: set of variable names in left-hand side."""
        return self.__lhs_vars

    @property
    def rhs_variables(self) -> FrozenSet[str]:
        """FrozenSet[str]: set of variable names in right-hand side."""
        return self.__rhs_vars

    @property
    def contextual_lhs(self) -> str:
        """str: Contextual name of assignment left-hand side."""
        return f"{self.__context.name}.{self.lhs}"

    @property
    def rhs(self) -> str:
        """str: Right-hand side of the assignment."""
        return self.__raw_sides[1]

    @rhs.setter
    def rhs(self, rhs: Any) -> None:
        context = self.eval_context
        lhs = self.lhs
        erhs = EvalString(rhs, context)
        raw_rhs = str(erhs)
        value = erhs.eval()
        if erhs.constant:
            rhs = EvalString.string(value)
        else:
            rhs = raw_rhs
        sides = EvalString(f"({lhs}, {rhs})", context)
        if self.__shape:
            if value is None:
                value = sides.eval()[1]
            if isinstance(value, Number):
                sides = EvalString(f"({lhs}, full_like({lhs}, {rhs}))", context)
            else:  # tentatively copy rhs into a numpy array
                self.__check_size(value)
                sides = EvalString(f"({lhs}, array({rhs}, dtype={self.__dtype}))", context)
        self.__sides = sides
        self.__constant = erhs.constant
        self.__rhs_vars = erhs.variables()
        self.__raw_sides[1] = raw_rhs

    @property
    def constant(self) -> bool:
        """bool: `True` if assignment right-hand side is constant, `False` otherwise."""
        return self.__constant

    def exec(self, context=None) -> Tuple[Any, bool]:
        """
        Evaluates rhs, and executes assignment lhs <- rhs.

        Returns
        -------
        Tuple[Any, bool]
            (rhs, changed), where 'changed' is True if the value of rhs has changed, False otherwise.
        """
        sides = self.__sides.eval()  # updates context at the same time
        changed = not numpy.array_equal(sides[0], sides[1])
        if context is None:
            context = self.__locals
        context['rhs_value'] = sides[1]
        exec(self.__code, dict(), context)
        return sides[1], changed

    @property
    def shape(self) -> Union[Tuple[int, int], None]:
        """Union[Tuple[int, int], None]: shape of assigned object (lhs) if it is an array, else None."""
        return self.__shape

    def variables(self) -> FrozenSet[str]:
        """Extracts all variables required for the assignment
        
        Returns
        -------
        FrozenSet[str]:
            Variable names as a set of strings
        """
        return self.__lhs_vars.union(self.__rhs_vars)

    def __str__(self) -> str:
        return " = ".join(self.__raw_sides)

    def __repr__(self) -> str:
        cls_name = self.__class__.__qualname__
        return "{}({!r}, {!r}, {})".format(cls_name, *self.__raw_sides, self.__context.name)

    def __check_size(self, array) -> None:
        """Checks if `array` is shape-compatible with lhs."""
        shape = self.__shape
        if numpy.shape(array) != shape:
            raise ValueError(f"Cannot assign {array} to array of shape {shape}")
