from collections.abc import MutableMapping
from numbers import Number
from typing import (
    Any, Dict, List, Optional, Callable,
    Iterator, TypeVar, Union, Tuple,
)

import numpy, numpy.polynomial

from cosapp.core.eval_str import EvalString
from cosapp.core.variableref import VariableReference
from cosapp.core.numerics.boundary import AbstractTimeUnknown, TimeUnknown
from cosapp.ports.port import ExtensiblePort
from cosapp.systems.system import System
from cosapp.utils.helpers import check_arg
from cosapp.drivers import Driver
from cosapp.drivers.time.scenario import TimeAssignString

T = TypeVar('T')


class TimeUnknownStack(AbstractTimeUnknown):
    """
    Class representing a group of variables [a, b, c, ...] jointly solved by a time driver, with
    b = da/dt, c = db/dt and so on. By nature, the unknown is therefore an array.
    If variables a, b, c... are arrays themselves, they are automatically flattened.

    Parameters
    ----------
    context : System
        System CoSApp in which all transients to be stacked are defined
    name : str
        Name of this time unknown stack
    transients : List[TimeUnknown]
        Stacked unknowns

    Notes
    -----
    The group variables must all be defined as variables of the same system.
    """
    def __init__(self,
        context: System,
        name: str,
        transients: List[TimeUnknown],
    ):
        super().__init__()
        self.__context = context
        self.__name = name
        self.__value = None
        self.__transients = transients
        self.__init_stack()

    @property
    def name(self) -> str:
        """str: Name of the variable"""
        return self.__name

    @property
    def context(self) -> System:
        """System: Evaluation context of the stacked unknown"""
        return self.__context

    @property
    def der(self) -> EvalString:
        """Expression of time derivative of stacked vector, given as an EvalString"""
        return self.__der

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__name} := {self!s}"

    def __init_stack(self) -> None:
        """
        1. Update the expression of the time derivative vector, and
        the size of individual variables (1 for scalars, n > 1 for vectors).
        It is assumed that all variables in the stack have the same size; in principle,
        this property is satisfied by design, since size consistency between a
        variable and its derivative is checked at declaration of all transient variables.
        
        2. Update the expression of max_time_step, defined as the minimum value of all
        individual maximum time steps (if any) defined by the stacked variables.
        """
        root = self.__transients[0].value

        size = len(root) if isinstance(root, (list, numpy.ndarray)) else 1
        # Init self.__value
        self.reset()

        expr = "asarray([{}]).ravel()"
        get_stack = lambda args: EvalString(expr.format(", ".join(args)), self.__context)
        self.__der = get_stack(map(lambda u: str(u.der), self.__transients))
        self.__var_size = size
        if size == 1:
            self.__sub_value = lambda offset: self.__value[offset]
        else:
            self.__sub_value = lambda offset: self.__value[offset : offset + size]

        # Set expressions of max time step and max absolute step
        def step_expr(mapping):
            args = ", ".join(map(mapping, self.__transients))
            return EvalString(f"min({args})", self.__context)
        self.__max_dt = step_expr(lambda var: str(var.max_time_step_expr))
        self.__max_dx = step_expr(lambda var: str(var.max_abs_step_expr))

    @property
    def value(self) -> numpy.ndarray:
        """numpy.ndarray: Value of the time unknown"""
        return self.__value

    @value.setter
    def value(self, new: Union[List[float], numpy.ndarray]) -> None:
        if numpy.shape(new) != self.__value.shape:
            raise ValueError("Incompatible array shapes")
        self.__value = numpy.array(new)
        # Update original system variables
        size = self.__var_size
        for i, unknown in enumerate(self.__transients):
            offset = i * size
            unknown.value = self.__sub_value(offset)

    def reset(self) -> None:
        """Reset stack value from original system variables"""
        self.__value = numpy.array(list(map(lambda t: t.value, self.__transients))).ravel()
        self.touch()

    def touch(self) -> None:
        """Set owner systems as 'dirty'."""
        for unknown in self.__transients:
            unknown.touch()

    @property
    def max_time_step_expr(self) -> EvalString:
        """EvalString: Expression of the maximum time step allowed for the instantaneous time evolution of the stacked variable"""
        return self.__max_dt

    @property
    def max_abs_step_expr(self) -> EvalString:
        """EvalString: Expression of the maximum step allowed for the stacked variable"""
        return self.__max_dx


class TimeUnknownDict(MutableMapping):
    """
    Dictionary of AbstractTimeUnknown objects, mapped to str variable names.
    Automatically updates a dictionary of time step constrained variables,
    accessible with read-only property `constrained`.
    """
    def __init__(self, **mapping):
        super().__init__()
        self.__transients = {}
        self.__constrained = {}
        self.update(mapping)

    def __str__(self) -> str:
        return str(self.__transients)

    def __repr__(self) -> str:
        return repr(self.__transients)

    def __len__(self) -> int:
        """int: length of the collection"""
        return len(self.__transients)

    def __getitem__(self, key: str) -> AbstractTimeUnknown:
        return self.__transients[key]

    def __setitem__(self, key: str, value: AbstractTimeUnknown) -> None:
        if not isinstance(key, str):
            raise TypeError(
                f"Keys of TimeUnknownDict must be strings; invalid key {key!r}"
            )
        if not isinstance(value, AbstractTimeUnknown):
            raise TypeError(
                "Elements of TimeUnknownDict must be of type AbstractTimeUnknown"
                f"; invalid item {key!r}: {type(value).__qualname__}"
            )
        self.__transients[key] = value
        if value.constrained:
            self.__constrained[key] = value
        else:
            try:
                self.__constrained.pop(key)
            except KeyError:
                pass

    def __delitem__(self, key: str) -> None:
        self.__transients.__delitem__(key)
        try:
            self.__constrained.__delitem__(key)
        except KeyError:
            pass

    def __contains__(self, key: str) -> bool:
        return key in self.__transients

    def __iter__(self) -> Iterator[str]:
        """Iterator on dictionary keys."""
        return iter(self.__transients)

    def __str__(self) -> str:
        return str(self.__transients)

    def __repr__(self) -> repr:
        return str(self.__transients)

    def keys(self, constrained=False) -> Iterator[str]:
        """Iterator on dictionary keys, akin to dict.keys().
        If `constrained` is True, the iterator applies only to time step constrained variables."""
        return self.__constrained.keys() if constrained else self.__transients.keys()

    def values(self, constrained=False) -> Iterator[AbstractTimeUnknown]:
        """Iterator on dictionary values, akin to dict.values().
        If `constrained` is True, the iterator applies only to time step constrained variables."""
        return self.__constrained.values() if constrained else self.__transients.values()

    def items(self, constrained=False) -> Iterator[Tuple[str, AbstractTimeUnknown]]:
        """Iterator on (key, value) tuples, akin to dict.items().
        If `constrained` is True, the iterator applies only to time step constrained variables."""
        return self.__constrained.items() if constrained else self.__transients.items()

    def get(self, key: str, *default: Optional[Any]) -> AbstractTimeUnknown:
        """Get value associated to `key`. Behaves as dict.get()."""
        return self.__transients.get(key, *default)

    def pop(self, key: str, *default: Optional[Any]) -> AbstractTimeUnknown:
        """Pop value associated to `key`. Behaves as dict.pop()."""
        try:
            self.__constrained.pop(key)
        except KeyError:
            pass
        finally:
            return self.__transients.pop(key, *default)

    def update(self, mapping: Dict) -> None:
        for key, value in mapping.items():
            self.__setitem__(key, value)

    def clear(self) -> None:
        self.__transients.clear()
        self.__constrained.clear()

    def max_time_step(self) -> float:
        """
        Compute maximum admissible time step, from transients' max_time_step (inf by default).
        Raises ValueError if any transients' max_time_step is not strictly positive.
        """
        dt = numpy.inf
        for name, transient in self.__constrained.items():
            max_dt = transient.max_time_step
            if max_dt <= 0:
                raise RuntimeError(
                    f"The maximum time step of {name} was evaluated to non-positive value {max_dt}"
                )
            dt = min(dt, max_dt)
        return dt

    @property
    def constrained(self) -> Dict[str, AbstractTimeUnknown]:
        """Dict[str, AbstractTimeUnknown]: shallow copy of the subset of time step constrained variables."""
        return self.__constrained.copy()


class TimeVarManager:
    """
    Class dedicated to the analysis of a system's independent transient variables.
    For example, in a system where

    .. math::

       dH/dt = f(a, b),

       dx/dt = v,

       dv/dt = a,

    the manager will identify two independent variables H and [x, v], with time derivatives
    f(a, b) and [v, a], respectively. Variable [x, v] and its derivative are handled by class
    `TimeUnknownStack`.
    """
    def __init__(self, context: System):
        self.context = context

    @property
    def context(self) -> System:
        """System handled by manager"""
        return self.__context

    @property
    def problem(self) -> "MathematicalProblem":
        """Mathematical problem handled by manager"""
        return self.__problem

    @context.setter
    def context(self, context: System):
        if not isinstance(context, System):
            raise TypeError("TimeVarManager context must be a system")
        self.__context = context
        self.update_transients()

    @property
    def transients(self) -> TimeUnknownDict:
        """
        Dictionary of all transient variables in current system, linking each
        variable (key) to its associated time unknown (value).
        For stand-alone, order-1 derivatives, transient unknowns are of type `TimeUnknown`.
        For higher-order derivatives, related variables are gathered into a `TimeUnknownStack` object.
        """
        return self.__transients

    @property
    def rates(self) -> Dict[str, "TimeDerivative"]:
        """
        Dictionary of all rate variables in current system, linking each
        variable (key) to its associated TimeDerivative object (value).
        """
        return self.__problem.rates

    def update_transients(self) -> None:
        """Update the transient variable dictionary (see property `transients` for details)"""
        context = self.__context
        problem = context.get_unsolved_problem()
        context_transients = problem.transients
        ders = dict()
        reference2name = dict()
        for name, unknown in context_transients.items():
            reference = unknown.pulled_from or unknown.context.name2variable[unknown.name]
            reference2name[reference] = name
            der_context = unknown.der.eval_context
            derivative_expr = str(unknown.der)
            try:
                ders[reference] = der_context.name2variable[derivative_expr]
            except KeyError:   # Complex derivative expression
                ders[reference] = VariableReference(context=der_context, mapping=None, key=derivative_expr)

        transients = TimeUnknownDict()
        # Comparison is done with VariableReference as
        # syst.name2variable["phi"] == syst.name2variable["inwards.phi"]
        tree = self.get_tree(ders)
        for root, branch in tree.items():
            if len(branch) > 2:  # second- or higher-order derivative -> build unknown stack
                stack_context = root.context
                branches = list(map(TimeVarManager._get_variable_fullname, branch[:-1]))
                root_stack_name = ", ".join(branches).join("[]")
                context_name = context.get_path_to_child(stack_context)
                stack_name = f"{context_name}{root_stack_name}"
                transients_stack = map(
                    lambda name: context_transients[name], 
                    map(lambda reference: reference2name[reference], branch[:-1])
                )
                transients[stack_name] = TimeUnknownStack(
                    stack_context, stack_name, list(transients_stack))
            else:  # first-order time derivative -> use current unknown
                root_name = reference2name[root]
                transients[root_name] = context_transients[root_name]

        self.__transients = transients
        self.__problem = problem

    @staticmethod
    def _get_variable_fullname(ref: VariableReference) -> str:
        """Built the variable fullname for its reference.
        
        Parameters
        ----------
        ref : VariableReference
            Reference to the variable
        
        Returns
        -------
        str
            The variable fullname
        """
        # First condition is to handle complex derivative expression see previous loop
        if ref.mapping is None or isinstance(ref.mapping, ExtensiblePort):
            return ref.key
        else:
            return f"{ref.mapping.name}.{ref.key}"

    @staticmethod
    def get_tree(ders: Dict[T, T]) -> Dict[T, List[T]]:
        """
        Parse a dictionary of the kind (var, d(var)/dt), to detect a dependency
        chain from one root variable to its successive time derivatives.
        Returns a dictionary of the kind:
        (root var 'X', [X_0, X_1, .., X_n]), where X_n is the expression of
        the nth-order time derivative of X.
        """
        var_list = ders.keys()
        der_list = ders.values()
        roots = list(filter(lambda var: var not in der_list, var_list))
        leaves = list(filter(lambda der: der not in var_list, der_list))
        tree = dict()
        for root in roots:
            tree[root] = [root]
            var = root
            while ders[var] not in leaves:
                der = ders[var]
                tree[root].append(der)
                var = der
            tree[root].append(ders[var])
        return tree

    def max_time_step(self) -> float:
        """
        Compute maximum admissible time step, from transients' `max_time_step` (numpy.inf by default).
        Raises ValueError if any transients' max_time_step is not strictly positive.
        """
        return self.__transients.max_time_step()


class TimeStepManager:
    """
    Class dedicated to the management of time step for time drivers.
    """
    def __init__(self, transients=TimeUnknownDict(), dt=None, max_growth_rate=None):
        self.__dt = None
        self.__nominal_dt = None
        self.__transients = None
        self.__growthrate = None
        # Assign initial values
        self.transients = transients
        self.nominal_dt = dt
        self.max_growth_rate = max_growth_rate

    @property
    def transients(self):
        return self.__transients

    @transients.setter
    def transients(self, transients: TimeUnknownDict):
        check_arg(transients, "transients", TimeUnknownDict)
        self.__transients = transients

    @property
    def nominal_dt(self) -> Number:
        """Time step"""
        return self.__nominal_dt

    @nominal_dt.setter
    def nominal_dt(self, value: Number) -> None:
        if value is not None:
            check_arg(value, 'dt', Number, value_ok = lambda dt: dt > 0)
        self.__nominal_dt = value

    @property
    def max_growth_rate(self) -> Number:
        """Maximum growth rate of time step"""
        return self.__growthrate

    @max_growth_rate.setter
    def max_growth_rate(self, value: Number) -> None:
        if value is None:
            self.__growthrate = numpy.inf
        else:
            check_arg(value, 'max_growth_rate', Number, value_ok = lambda x: x > 1)
            self.__growthrate = value

    def max_time_step(self) -> float:
        """
        Compute maximum admissible time step, from transients' max_time_step (inf by default).
        Raises ValueError if any transients' max_time_step is not strictly positive.
        """
        return self.__transients.max_time_step()

    def time_step(self, previous=None) -> float:
        """
        Compute time step, making sure that it does not exceed any transient's `max_time_step`
        (numpy.inf by default), and that all transient max_time_step are strictly positive.
        If `previous` is specified, the returned time step is bounded by max_growth_rate * previous.

        An exception is raised if time step is ultimately found to be infinity.
        """
        dt = self.__nominal_dt or numpy.inf
        dt = min(dt, self.max_time_step())
        if previous is not None and previous > 0:
            dt = min(dt, self.__growthrate * previous)

        if not numpy.isfinite(dt):
            raise ValueError("Time step was not specified, and could not be determined from transient variables")

        return dt


def TwoPointCubicPolynomial(
    xs: Tuple[float, float],
    ys: Tuple[float, float],
    dy: Tuple[float, float],
) -> numpy.polynomial.Polynomial:
    """Function returning a cubic polynomial interpolating
    two end points (x, y), with imposed derivatives dy/dx.

    Arguments:
    ----------
    - xs, Tuple[float, float]: end point abscissa
    - ys, Tuple[float, float]: end point values
    - dy, Tuple[float, float]: end point derivatives

    Returns:
    --------
    poly: cubic numpy.polynomial.Polynomial function
    """
    h = xs[1] - xs[0]
    h2 = h * h
    mat = numpy.array(
        [
            [h, h2, h * h2],
            [1, 0, 0],
            [1, 2 * h, 3 * h2],
        ],
        dtype=float,
    )
    coefs = numpy.zeros(4)
    coefs[0] = ys[0]
    coefs[1:] = numpy.linalg.solve(mat, [ys[1] - ys[0], *dy])
    return numpy.polynomial.Polynomial(coefs, xs, [0, h])


def TwoPointCubicInterpolator(
    xs: Tuple[float, float],
    ys: numpy.ndarray,
    dy: numpy.ndarray,
) -> Callable[[float], Union[float, numpy.ndarray]]:
    """Function returning a cubic polynomial interpolator
    for either scalar or vector quantities, based on the
    format of input arrays `ys` and `dy`.
    If `ys` and `dy` are 1D (resp. 2D) arrays, they are
    interpreted as the values and derivatives of a scalar
    (resp. vector) quantity at end points `xs`.

    Arguments:
    ----------
    - xs, Tuple[float, float]: end point abscissa
    - ys, numpy.ndarray: end point values as a 1D or 2D array
    - dy, numpy.ndarray: end point derivatives as a 1D or 2D array

    Returns:
    --------
    poly: cubic polynomial function returning either
        a float or a numpy array of floats, depending on
        the dimension of input data `ys` and `dy`.
    """
    if numpy.ndim(ys) == 1:
        return TwoPointCubicPolynomial(xs, ys, dy)
    ys = numpy.transpose(ys)
    dy = numpy.transpose(dy)
    # Multi-dimensional polynomial
    fs = [
        TwoPointCubicPolynomial(xs, val, der)
        for (val, der) in zip(ys, dy)
    ]
    def ndpoly(t: float) -> numpy.ndarray:
        return numpy.array([f(t) for f in fs])
    return ndpoly


class SystemInterpolator:
    """Class providing a continuous time view on a system,
    by replacing transient variables by time functions.
    """
    def __init__(self, driver: "ExplicitTimeDriver"):
        from cosapp.drivers.time.interfaces import ExplicitTimeDriver
        check_arg(driver, 'driver', ExplicitTimeDriver)
        self.__owner = driver
        self.__system = system = driver.owner
        problem = system.get_unsolved_problem()
        self.__transients = transients = problem.transients
        self.__interp = dict.fromkeys(transients, None)

    @property
    def system(self) -> System:
        """System modified by interpolator"""
        return self.__system

    @property
    def transients(self) -> Dict[str, TimeUnknown]:
        return self.__transients

    @property
    def interp(self) -> Dict[str, Callable]:
        """Dict[str, Callable]: interpolant dictionary"""
        return self.__interp

    @interp.setter
    def interp(self, interp: Dict[str, Callable]):
        transients = self.__transients
        check_arg(
            interp, "interp", dict,
            lambda d: set(d) == set(transients)
        )
        context = self.system
        for key, func in interp.items():
            self.__interp[key] = TimeAssignString(key, func, context)

    def exec(self, t: float) -> None:
        for assignment in self.__interp.values():
            assignment.exec(t)
        driver = self.__owner
        driver._set_time(t)
