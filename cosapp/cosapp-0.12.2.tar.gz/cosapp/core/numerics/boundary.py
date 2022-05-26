from numbers import Number
from typing import Any, Dict, Optional, Union, Tuple
from types import SimpleNamespace

import abc
import numpy

from cosapp.core.eval_str import EvalString
from cosapp.core.variableref import VariableReference
from cosapp.ports.enum import PortType
from cosapp.ports.exceptions import ScopeError
from cosapp.utils.parsing import get_indices
from cosapp.utils.helpers import check_arg


class Boundary:
    """Numerical solver boundary.

    Parameters
    ----------
    context : cosapp.systems.System
        System in which the boundary is defined.
    name : str
        Name of the boundary
    mask : numpy.ndarray or None
        Mask of the values in the vector boundary.
    default : Number, numpy.ndarray or None
        Default value to set the boundary with.
    """
    def __init__(self,
        context: "cosapp.systems.System",
        name: str,
        mask: Optional[numpy.ndarray] = None,
        default: Union[Number, numpy.ndarray, None] = None,
        **kwargs
    ):
        super().__init__(**kwargs)  # for collaborative inheritance
        self.__info = info = Boundary.parse(context, name, mask)

        self._context = context  # type: cosapp.systems.System
        self._default_value = None  # type: Union[Number, numpy.ndarray, None]

        self.mask = info.mask
        self.set_default_value(default, self.mask)

    @staticmethod
    def parse(
        context: "cosapp.systems.System",
        name: str,
        mask: Optional[numpy.ndarray] = None
    ) -> SimpleNamespace:
        """
        Parse port and variable name from a name and its evaluation context.
        Also checks that the variable belongs to an input port.

        Parameters
        ----------
        - context : cosapp.systems.System
            System in which the boundary is defined.
        - name : str
            Name of the boundary
        - mask : numpy.ndarray[bool] or None, optional
            Mask to apply on the variable; default is None (i.e. no mask)

        Returns
        -------
        info: SimpleNameSpace
            Structure containing fields `varname`, `fullname`, `port` and `mask`.
        """
        if not isinstance(name, str):
            raise TypeError(f"Variable name {type(name).__qualname__!r} is not a string.")

        var_name, auto_mask = get_indices(context, name)

        container = Boundary.container(context, var_name)

        # Force port name to be included in unknown name
        fullpath = var_name.split(".")
        if len(fullpath) < 2 or fullpath[-2] != container.name:
            fullpath.insert(-1, container.name)
        portname = ".".join(fullpath[:-1])

        return SimpleNamespace(
            varname = fullpath[-1],
            fullname = ".".join(fullpath),
            port = context[portname],
            mask = mask if mask is not None else auto_mask,
            ref = context.name2variable[var_name],
        )

    @staticmethod
    def container(system: "cosapp.systems.System", name: str) -> "BasePort":
        """
        Checks that variable `name` is a valid boundary in `system`.
        If so, returns the container port. Raises an exception otherwise.

        Parameters
        ----------
        - system: cosapp.systems.System
            System in which a boundary may be defined.
        - name: str
            Name of the variable to check
        
        Returns
        -------
        - container: BasePort
            Port containing the variable, if the latter is found valid (raises an exception otherwise)

        Raises
        ------
        - `AttributeError` if name is not found in system
        - `TypeError` if container is a sub-system (not a port)
        - `ValueError` if container is an output port
        - `ScopeError` if container port does not belong to system
        """
        from cosapp.ports.port import BasePort
        if name not in system:
            raise AttributeError(
                f"Variable {name!r} is not present in {system.name!r}."
            )

        _, container, key = system.name2variable[name]
        if not isinstance(container, BasePort):
            raise TypeError(
                f"Only variables can be used in mathematical algorithms; got {name!r} in {system.name!r}"
            )

        if not container.is_input:
            path =  f"{system.name}.{container.name}"
            raise ValueError(
                f"Only variables in input ports can be used as boundaries; got {name!r} in {path!r}."
            )

        # Test if the type and scoping are compatible with the boundary status
        try:
            container.validate(key, system[name])
        except ScopeError:  # Type error should still be raised
            if system is not container.owner:
                # Only owner can set its variables
                raise ScopeError(
                    f"Trying to set variable {name!r} out of your scope through a boundary."
                )
        return container

    def __str__(self) -> str:
        return str(self.default_value)

    def __repr__(self) -> str:
        return f"{self.name} := {self!s}"

    @property
    def context(self) -> "cosapp.systems.System":
        """cosapp.systems.System : System in which the boundary is defined."""
        return self._context

    @property
    def port(self) -> "BasePort":
        """BasePort: port containing the boundary."""
        return self.__info.port

    @property
    def name(self) -> str:
        """str : Contextual name of the boundary."""
        return self.__info.fullname

    @property
    def ref(self) -> VariableReference:
        """VariableReference : variable reference accessed by the boundary."""
        return self.__info.ref

    @property
    def variable(self) -> str:
        """str : name of the variable accessed by the boundary."""
        return self.__info.varname

    @property
    def mask(self) -> Optional[numpy.ndarray]:
        """numpy.ndarray or None : Mask of the values in the vector boundary."""
        return self.__info.mask

    @mask.setter
    def mask(self, mask: Union[None, numpy.ndarray]) -> None:
        check_arg(mask, f"mask for variable {self.name!r}", (type(None), list, tuple, numpy.ndarray))
        if mask is not None:
            mask = numpy.asarray(mask)
            value_array = numpy.asarray(self.ref.value)
            if value_array.ndim == 0:
                if mask.size != 1:
                    raise ValueError(
                        "Mask for variable {!r} should have size 1; got {} elements.".format(
                            self.name, mask.size
                        )
                    )
                if numpy.all(mask):
                    mask = None
            elif mask.shape != value_array.shape:
                raise ValueError(
                    "Mask shape {} for variable {!r} is wrong; expected {}.".format(
                        mask.shape, self.name, value_array.shape
                    )
                )
        self.__info.mask = mask

    @property
    def value(self) -> Union[Number, numpy.ndarray]:
        """Number or numpy.ndarray: Current value of the boundary."""
        value = self.__info.ref.value
        if self.mask is None:
            return value
        elif numpy.any(self.mask):
            return value[self.mask]
        else:
            return numpy.empty(0)

    @value.setter
    def value(self, new: Union[Number, numpy.ndarray]) -> None:
        ref = self.__info.ref

        if self.mask is None:
            if not numpy.array_equal(ref.value, new):
                ref.value = new
                self.touch()
        elif numpy.any(self.mask) and not numpy.array_equal(ref.value[self.mask], new):
            ref.value[self.mask] = new
            self.touch()

    def touch(self) -> None:
        """Set owner system as 'dirty'."""
        self.__info.port.owner.set_dirty(PortType.IN)

    @property
    def default_value(self) -> Union[Number, numpy.ndarray, None]:
        """Number, numpy.ndarray or None: default value for the boundary."""
        if self._default_value is None or self.mask is None:
            return self._default_value
        else:
            return self._default_value[self.mask]

    def set_default_value(self,
        value: Union[Number, numpy.ndarray, None],
        mask: Optional[numpy.ndarray] = None
    ) -> None:
        """Set the default value.

        Parameters
        ----------
        value : Number, numpy.ndarray or None
            Default value
        mask : numpy.ndarray[bool] or None, optional
            Mask to apply on the default value; default None (i.e. no mask)
        """
        if value is None:
            self._default_value = None
            return

        default_array = numpy.asarray(value)
        value_array = numpy.asarray(self.ref.value)
        if mask is not None:
            if mask.shape != self.mask.shape:
                raise ValueError(
                    f"Provided mask shape {mask.shape} does not match current value shape {self.mask.shape}."
                )
            # Extend singleton in array or fill with nan masked default
            if mask.shape != default_array.shape:
                tmp = numpy.full_like(mask, numpy.nan, dtype=default_array.dtype)
                tmp[mask] = default_array
                default_array = tmp
            else:
                default_array = numpy.where(mask, default_array, value_array)
        elif self.mask is not None:
            if default_array.size == value_array[self.mask].size:
                tmp = numpy.full_like(value_array, numpy.nan)
                tmp[self.mask] = default_array
                default_array = tmp

            if default_array.ndim == 0:  # We have a single value masked
                self._default_value = None
                return
            mask = self.mask.copy()

        if value_array.shape != default_array.shape:
            raise ValueError(
                f"Default value {value} has not the same shape as value {self.value}."
            )

        if self.default_value is not None:
            old_mask = numpy.isfinite(self._default_value)

            default_array, mask = self._merge_masked_array(
                default_array, mask, self._default_value, old_mask)

            self.mask = mask

        elif mask is not None:
            self.mask = numpy.ma.make_mask(numpy.logical_or(mask, self.mask))

        self._default_value = default_array if default_array.ndim > 0 else default_array.tolist()

    @staticmethod
    def _merge_masked_array(
        value: Union[Number, numpy.ndarray],
        mask: Optional[numpy.ndarray],
        old_value: Union[Number, numpy.ndarray],
        old_mask: Optional[numpy.ndarray],
    ) -> Tuple[numpy.ndarray, Optional[numpy.ndarray]]:
        """Merge the old masked array with the new one.

        Parameters
        ----------
        value : Union[Number, numpy.ndarray]
            New value
        mask : Optional[numpy.ndarray]
            New mask
        old_value : Union[Number, numpy.ndarray]
            Old value
        old_mask : Optional[numpy.ndarray]
            Old mask

        Returns
        -------
        (numpy.ndarray, numpy.ndarray or None)
            The merged array with the resulting mask.
        """
        if mask is not None:
            if old_mask is not None:
                old_value = numpy.asarray(old_value)
                tmp = numpy.full_like(mask, numpy.nan, dtype=old_value.dtype)
                tmp[old_mask] = old_value[old_mask]
                tmp[mask] = value[mask]
                value = tmp
                mask = numpy.logical_or(old_mask, mask)
            else:  # An homogeneous value is set
                value[~mask] = old_value
                mask = None  # None specified indices are set to the old value
        return value, mask

    def set_to_default(self) -> None:
        """Set the current value with the default one."""
        if self._default_value is None:
            # This is to verbose and not understable with a classical use
            # logger.warning(f"No default value given for variable '{self.context.name}.{self.name}'. It will be skipped.")
            return

        nan_mask = numpy.isfinite(self._default_value)
        if self.mask is None:
            if numpy.all(nan_mask):
                self.value = self.default_value
            else:
                self.value[nan_mask] = self.default_value[nan_mask]
        else:
            sub_mask = nan_mask[self.mask]
            if numpy.all(sub_mask):
                self.value = self.default_value
            else:
                self.value[sub_mask] = self.default_value[sub_mask]


class Unknown(Boundary):
    """Numerical solver unknown.

    Parameters
    ----------
    context : cosapp.systems.System
        System in which the unknown is defined.
    name : str
        Name of the unknown
    lower_bound : float
        Minimum value authorized; default -numpy.inf
    upper_bound : float
        Maximum value authorized; default numpy.inf
    max_abs_step : float
        Max absolute step authorized in one iteration; default numpy.inf
    max_rel_step : float
        Max relative step authorized in one iteration; default numpy.inf
    mask : numpy.ndarray or None
        Mask of unknown values in the vector variable.

    Attributes
    ----------
    lower_bound : float
        Minimum value authorized; default -numpy.inf
    upper_bound : float
        Maximum value authorized; default numpy.inf
    max_abs_step : float
        Largest absolute step authorized in one iteration; default numpy.inf
    max_rel_step : float
        Largest relative step authorized in one iteration; default numpy.inf

    Notes
    -----
    The dimensionality of the variable should be taken into account in the bounding process.
    """

    def __init__(self,
        context: "cosapp.systems.System",
        name: str,
        # absolute_step: Number = 1.5e-8,  # TODO ?
        # relative_step: Number = 1.5e-8,  # TODO ?
        max_abs_step: Number = numpy.inf,
        max_rel_step: Number = numpy.inf,
        lower_bound: Number = -numpy.inf,
        upper_bound: Number = numpy.inf,
        # reference: Union[Number, numpy.ndarray] = 1.,  # TODO normalize unknown
        mask: Optional[numpy.ndarray] = None,
    ):
        super().__init__(context, name, mask)

        check_arg(max_abs_step, 'max_abs_step', Number, lambda x: x > 0)
        check_arg(max_rel_step, 'max_rel_step', Number, lambda x: x > 0)
        check_arg(lower_bound, 'lower_bound', Number)
        check_arg(upper_bound, 'upper_bound', Number)

        # TODO take into account the variable dimension in the constructor ?
        self.lower_bound = lower_bound  # type: Number
        self.upper_bound = upper_bound  # type: Number
        self.max_abs_step = max_abs_step  # type: Number
        self.max_rel_step = max_rel_step  # type: Number

    def __str__(self) -> str:
        try:
            return str(self.value)
        except KeyError:  # boundary does not exist in the current context
            return str(self.default_value)

    def copy(self) -> "Unknown":
        """Copy the unknown object.

        Returns
        -------
        Unknown
            Duplicated unknown
        """
        return self.transfer(self.context, self.name)

    def transfer(self, context: "cosapp.systems.System", name: str) -> "Unknown":
        """Transfer a copy of the unknown in a new context.

        Returns
        -------
        Unknown
            Duplicated unknown, in new context
        """
        new = Unknown(
            context,
            name,
            max_abs_step=self.max_abs_step,
            max_rel_step=self.max_rel_step,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
        )
        new.mask = None if self.mask is None else self.mask.copy()
        return new

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSONable representation of the unknown.
        
        Returns
        -------
        Dict[str, Any]
            JSONable representation
        """
        return {
            "context": self.context.contextual_name,
            "name": self.name,
            "max_abs_step": self.max_abs_step,
            "max_rel_step": self.max_rel_step,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "mask": None if self.mask is None else self.mask.tolist()
        }


class AbstractTimeUnknown(abc.ABC):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # for collaborative inheritance

    @abc.abstractproperty
    def der(self) -> EvalString:
        """Expression of the time derivative, given as an EvalString"""
        pass

    @abc.abstractproperty
    def max_time_step_expr(self) -> EvalString:
        """Expression of the maximum admissible time step, given as an EvalString."""
        pass

    @abc.abstractproperty
    def max_abs_step_expr(self) -> EvalString:
        """Expression of the maximum absolute step in one iteration, given as an EvalString."""
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset transient unknown to a reference value"""
        pass

    @property
    def d_dt(self) -> Any:
        """Value of time derivative"""
        return self.der.eval()

    @property
    def max_abs_step(self) -> float:
        """float: Maximum absolute step in one iteration"""
        return self.max_abs_step_expr.eval()

    @property
    def max_time_step(self) -> float:
        """float: Maximum admissible time step in one iteration"""
        dt_max = self.max_time_step_expr.eval()
        dx_max = self.max_abs_step
        if numpy.isfinite(dx_max):
            step_based_dt = self.extrapolated_time_step(dx_max)
            dt_max = min(dt_max, step_based_dt)
        return dt_max

    @property
    def constrained(self) -> bool:
        """bool: is unknown constrained by a limiting time step?"""
        constrained = lambda expr: numpy.isfinite(expr.eval()) if expr.constant else True
        return constrained(self.max_time_step_expr) or constrained(self.max_abs_step_expr)

    def extrapolated_time_step(self, step: float) -> float:
        """
        Time step necessary to attain a variation of `step`
        at a rate given by current value of the time derivative.
        """
        rate = numpy.abs(self.d_dt)
        step = numpy.where(rate > 0, abs(step), numpy.inf)
        rate = numpy.where(rate > 0, rate, 1)
        return numpy.min(step / rate)


class TimeUnknown(Boundary, AbstractTimeUnknown):
    """Time-dependent solver unknown.

    Parameters
    ----------
    context : cosapp.systems.System
        System in which the unknown is defined.
    name : str
        Name of the unknown

    Attributes
    ----------
    max_time_step : float
        Max time step authorized in one iteration; default numpy.inf
    """

    def __init__(self,
        context: "cosapp.systems.System",
        name: str,
        der: Any,
        max_time_step: Union[Number, str] = numpy.inf,
        max_abs_step: Union[Number, str] = numpy.inf,
        pulled_from: Optional[VariableReference] = None,
    ):
        super().__init__(context, name)
        self._pulled_from = pulled_from
        self.__type = None
        self.__shape = None
        self.__dt_max = numpy.inf
        self.__dx_max = numpy.inf
        self.d_dt = der
        self.max_time_step = max_time_step
        self.max_abs_step = max_abs_step

    def __str__(self) -> str:
        try:
            return str(self.value)
        except KeyError:  # does not exist in current context
            return str(self.default_value)

    @property
    def der(self) -> EvalString:
        """Expression of time derivative, given as an EvalString"""
        return self.__der

    @AbstractTimeUnknown.d_dt.setter
    def d_dt(self, expression: Any):
        eval_string, value, dtype = self.der_type(expression, self.context)
        if self.__type is None:
            self.__type = dtype
            if dtype is numpy.ndarray:
                self.__shape = value.shape
            elif dtype is not Number:
                raise TypeError(
                    f"Derivative expressions may only be numbers or array-like collections; got '{value}'")
        elif self.__type is not dtype:
            raise TypeError(
                f"Expression '{expression!s}' is incompatible with declared type {self.__type.__qualname__}")
        if self.__shape and numpy.shape(value) != self.__shape:
            raise ValueError(
                f"Expression '{expression!s}' should be an array of shape {self.__shape}")
        self.__der = eval_string

    @property
    def max_time_step_expr(self) -> EvalString:
        """Maximum admissible time step, given as an EvalString."""
        return self.__dt_max

    @property
    def max_abs_step_expr(self) -> EvalString:
        """Maximum admissible step, given as an EvalString."""
        return self.__dx_max

    @AbstractTimeUnknown.max_time_step.setter
    def max_time_step(self, expression: Any):
        self.__dt_max = self.__positive_expr(expression, "max_time_step")

    @AbstractTimeUnknown.max_abs_step.setter
    def max_abs_step(self, expression: Any):
        self.__dx_max = self.__positive_expr(expression, "max_abs_step")

    def __positive_expr(self, expression: Any, name: str) -> EvalString:
        eval_string, value, dtype = self.der_type(expression, self.context)
        check_arg(value, name, Number)  # checks that expression is scalar
        if value <= 0 and eval_string.constant:
            # Note:
            #   If expression is context-dependent (non-constant), it may turn out to be positive at time driver execution.
            #   Therefore, an exception should only be raised for constant, non-positive expressions.
            raise ValueError(f"{name} must be strictly positive")
        return eval_string

    def copy(self) -> "TimeUnknown":
        """Copy time-dependent unknown object.

        Returns
        -------
        TimeUnknown
            Duplicated unknown
        """
        return TimeUnknown(self.context, self.name, self.der, self.max_time_step_expr)

    @staticmethod
    def der_type(expression: Any, context: "cosapp.systems.System") -> Tuple:
        """Static method to evaluate the type and default value of an expression used as time derivative"""
        if isinstance(expression, EvalString):
            eval_string = expression
        else:
            eval_string = EvalString(expression, context)
        value = eval_string.eval()
        if isinstance(value, (list, tuple, numpy.ndarray)):
            value = numpy.array(value)
            dtype = numpy.ndarray
        elif TimeUnknown.is_number(value):
            dtype = Number
        else:
            dtype = type(value)
        return eval_string, value, dtype

    @staticmethod
    def is_number(value) -> bool:
        """Is value suitable for a derivative?"""
        return isinstance(value, Number) and not isinstance(value, bool)

    @property
    def pulled_from(self) -> Optional[VariableReference]:
        """VariableReference or None: Original time unknown before pulling; None otherwise."""
        return self._pulled_from

    @Boundary.value.setter
    def value(self, new: Union[Number, numpy.ndarray]) -> None:
        super(self.__class__, self.__class__).value.fset(self, new)
        self.touch()

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSONable representation of the transient unknown.
        
        Returns
        -------
        Dict[str, Any]
            JSONable representation
        """
        return {
            "context": self.context.contextual_name,
            "name": self.name,
            "der": str(self.__der),
            "max_time_step": str(self.max_time_step_expr),
        }

    def reset(self) -> None:
        """Reset transient unknown to a reference value.
        Inactive for class TimeUnknown."""
        pass


class TimeDerivative(Boundary):
    """Explicit time derivative.

    Parameters
    ----------
    context : cosapp.systems.System
        System in which the unknown is defined.
    name : str
        Name of the variable
    source : str
        Variable such that name = d(source)/dt
    initial_value : Any
        Time derivative initial value
    """

    def __init__(self,
        context: "cosapp.systems.System",
        name: str,
        source: Any,
        initial_value: Any = None,
    ):
        super().__init__(context, name)
        self.__shape = None
        self.__previous = None
        eval_string, value, self.__type = self.source_type(source, self.context)
        if self.__type is numpy.ndarray:
            self.__shape = value.shape
        # Set source & initial value
        self.source = source
        self.initial_value = initial_value
        self.reset()

    def __str__(self) -> str:
        try:
            return str(self.value)
        except KeyError:  # does not exist in current context
            return str(self.default_value)

    def reset(self, value: Any = None) -> None:
        self.__previous = self.source
        if value is not None:
            self.initial_value = value  # NB: `value` may be an expression
        value = self.initial_value
        if value is not None:
            self.__set_value(value)

    @property
    def source_expr(self) -> EvalString:
        """Variable whose rate is evaluated, returned as an EvalString"""
        return self.__src

    @property
    def source(self) -> Union[Number, numpy.ndarray]:
        """Value of the variable whose rate is evaluated"""
        return self.__src.eval()

    @source.setter
    def source(self, expression: Any):
        self.__src = self.__parse(expression)
        if self.__previous is None:
            self.__previous = self.source

    @property
    def initial_value_expr(self) -> EvalString:
        """Initial value of time derivative, returned as an EvalString"""
        return self.__initial

    @property
    def initial_value(self) -> Union[Number, numpy.ndarray]:
        """Initial value of time derivative"""
        return self.__initial.eval()

    @initial_value.setter
    def initial_value(self, expression):
        if expression is None:
            self.__initial = EvalString(None, self.context)
        else:
            self.__initial = self.__parse(expression)

    def update(self, dt: Number) -> Number:
        """Evaluate rate-of-change of source over time interval `dt`"""
        current = self.source
        rate = (current - self.__previous) / dt  # backward finite-difference time derivative
        self.__set_value(rate)
        self.__previous = current
        return rate

    def __set_value(self, value: Union[Number, numpy.ndarray]):
        """Private setter for `value`"""
        super(self.__class__, self.__class__).value.fset(self, value)
        self.touch()

    @Boundary.value.setter
    def value(self, new: Union[Number, numpy.ndarray]) -> None:
        raise RuntimeError("Time derivatives are computed, and cannot be explicitly set")

    @staticmethod
    def source_type(expression: Any, context: "cosapp.systems.System") -> Tuple:
        """Static method to evaluate the type and default value of an expression used as rate source"""
        eval_string, value, dtype = TimeUnknown.der_type(expression, context)
        if dtype is numpy.ndarray:
            value.fill(0.0)
        else:
            value = 0.0
        return eval_string, value, dtype

    def __parse(self, expression: Any) -> EvalString:
        eval_string, value, dtype = TimeUnknown.der_type(expression, self.context)
        if self.__type is not dtype:
            raise TypeError(
                f"Expression '{expression!s}' is incompatible with declared type {self.__type.__qualname__}")
        if self.__shape and value.shape != self.__shape:
            raise ValueError(f"Expression '{expression!s}' should be an array of shape {self.__shape}")
        return eval_string

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSONable representation of the time derivative.
        
        Returns
        -------
        Dict[str, Any]
            JSONable representation
        """
        return {
            "context": self.context.contextual_name,
            "name": self.name,
            "source": str(self.source_expr),
            "initial_value": str(self.initial_value_expr),
        }
