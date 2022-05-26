"""This module define the basic class encapsulating a variable attributes."""
import abc
import array
import numpy
import logging
import copy
from collections.abc import MutableSequence
from numbers import Number
from typing import Any, Dict, Iterable, Optional, Tuple, Union, NoReturn

from cosapp.ports import units
from cosapp.ports.enum import Scope, Validity, RangeType
from cosapp.utils.distributions import Distribution
from cosapp.utils.naming import NameChecker, CommonPorts
from cosapp.utils.helpers import check_arg, is_numerical, get_typename

logger = logging.getLogger(__name__)

RangeValue = Optional[Tuple[Any, Any]]
ArrayIndices = Optional[Union[int, Iterable[int], Iterable[Iterable[int]], slice]]
Types = Optional[Union[Any, Tuple[Any, ...]]]


class BaseVariable(abc.ABC):
    """Base class for variable detail container.

    Parameters
    ----------
    - name [str]:
        Variable name.
    - port [BasePort]:
        Port to which variable belongs.
    - value [Any]:
        Variable value.
    - unit [str, optional]:
        Variable unit; default empty string (i.e. dimensionless)
    - dtype [type or iterable of type, optional]:
        Variable type; default None (i.e. type of initial value).
    - desc [str, optional]:
        Variable description; default to ''.
    - scope [Scope]: {PRIVATE, PROTECTED, PUBLIC},
        Variable visibility; defaults to PRIVATE.
    """

    # Value cannot be integrated in this object
    #   otherwise value getter execution time *200
    #   another advantage is that the metadata can be change/shared without providing
    #     a way to change the value no passing through the Port (which is bad for the
    #     clean dirty logic).
    #   Disadvantage : the logic to store the details and the value is a bit messy in
    #     BasePort.add_variable

    __slots__ = (
        "__weakref__",
        "_name",
        "_desc",
        "_unit",
        "_port",
        "_scope",
        "_dtype",
    )

    __name_check = NameChecker(excluded=CommonPorts.names())

    def __init__(
        self,
        name: str,
        port: "cosapp.ports.port.BasePort",
        value: Any,
        unit: str = "",
        dtype: Types = None,
        desc: str = "",
        scope: Scope = Scope.PRIVATE,
    ):
        self._name = self.name_check(name)

        from cosapp.ports.port import BasePort
        check_arg(port, 'port', BasePort)
        self._port = port

        check_arg(unit, 'unit', str)
        if dtype is not None:
            if not isinstance(dtype, type):
                failed = False
                try:
                    for dtype_ in dtype:
                        failed |= not isinstance(dtype_, type)
                except TypeError:
                    failed = True
                if failed:
                    raise TypeError(f"Types must be defined by a type; got {dtype}.")

        check_arg(desc, 'desc', str)
        check_arg(scope, 'scope', Scope)
        
        if unit and not is_numerical(value):
            unit = ""
            logger.warning(
                f"A physical unit is defined for non-numerical variable {name!r}; it will be ignored."
            )

        elif not units.is_valid_units(unit) and unit:
            raise units.UnitError(f"Unknown unit {unit}.")

        value, dtype = self._process_value(value, dtype)

        self._unit = unit  # type: str
        self._desc = desc  # type: str
        self._dtype = dtype  # type: Types
        self._scope = scope  # type: Scope

    @abc.abstractmethod
    def copy(self, port: "BasePort", name: Optional[str] = None) -> "BaseVariable":
        pass

    @abc.abstractmethod
    def _repr_markdown_(self) -> str:
        """Returns the representation of this variable in Markdown format.

        Returns
        -------
        str
            Markdown formatted representation
        """
        pass

    def _process_value(self, value, dtype):
        if dtype is None:
            if value is None:
                dtype = None  # can't figure out type if both value and dtype are None
            else:
                dtype = type(value)
                if is_numerical(value):
                    # Force generic number type only if user has not specified any type
                    if issubclass(dtype, Number):
                        dtype = (Number, numpy.ndarray)
                    elif isinstance(value, (MutableSequence, array.ArrayType)):
                        # We have a collection => transform Mutable to ndarray
                        dtype = (MutableSequence, array.ArrayType, numpy.ndarray)
                        value = numpy.asarray(value)

        elif value is not None:
            # Test value has the right type
            if not isinstance(value, dtype):
                typename = get_typename(dtype)
                raise TypeError(
                    "Cannot set {} of type {} with a {}.".format(
                        self.full_name, typename, type(value).__qualname__,
                    )
                )

        return value, dtype

    @classmethod
    def name_check(cls, name: str):
        return cls.__name_check(name)

    @property
    def full_name(self) -> str:
        return f"{self._port.contextual_name}.{self.name}"

    @property
    def name(self) -> str:
        """str : Variable name"""
        return self._name

    @property
    def value(self) -> Any:
        return getattr(self._port, self._name)

    # @value.setter
    # def value(self, value) -> None:
    #     setattr(self._port, self._name, value)

    @property
    def unit(self) -> str:
        """str : Variable unit; empty string means dimensionless"""
        return self._unit

    @property
    def dtype(self) -> Types:
        """Type[Any] or Tuple of Type[Any] or None : Type of the variable; default None (i.e. type of default value is set)"""
        return self._dtype

    @property
    def description(self) -> str:
        """str : Variable description"""
        return self._desc

    @property
    def scope(self) -> Scope:
        """Scope : Scope of variable visibility"""
        return self._scope

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self._repr_markdown_()
    
    def __json__(self) -> Dict[str, Any]:
        """JSONable dictionary representing a variable.
        
        Returns
        -------
        Dict[str, Any]
            The dictionary
        """
        return {
            "value": self.value,
        }

    def filter_value(self, value: Any) -> Any:
        if self.dtype == (
            MutableSequence,
            array.ArrayType,
            numpy.ndarray,
        ):
            value = numpy.asarray(value)
        return value

    def _to_raw_dict(self) -> Dict[str, Any]:
        """Convert this variable into a dictionary.
   
        Returns
        -------
        dict
            The dictionary representing this variable.
        """
        return {
            "value" : self.value,
            "unit": self.unit or None,
            "desc" : self.description or None,
        }

    def to_dict(self) -> Dict:
        """Convert this variable into a dictionary.
   
        Returns
        -------
        Dict[str, Any]:
            Dictionary representing variable. Attributes with `None` value are filtered out.
        """
        data = self._to_raw_dict()
        return dict(filter(
            lambda items: items[1] is not None,
            data.items()
        ))


class Variable(BaseVariable):
    """Variable detail container.

    The `valid_range` defines the range of value for which a model is known to behave correctly.
    The `limits` are at least as large as the validity range.

    Parameters
    ----------
    - name [str]:
        Variable name.
    - port [BasePort]:
        Port to which variable belongs.
    - value [Any]:
        Variable value.
    - unit [str, optional]:
        Variable unit; default empty string (i.e. dimensionless)
    - dtype [type or iterable of type, optional]:
        Variable type; default None (i.e. type of initial value).
    - desc [str, optional]:
        Variable description; default to ''.
    - valid_range [Tuple[Any, Any] or Tuple[Tuple], optional]:
        Validity range of the variable; default None (i.e. all values are valid).
        Tuple[Any, Any] in case of scalar value, tuple of tuples in case of vector value.
    - invalid_comment [str, optional]:
        Comment to show in case the value is not valid; default ''
    - limits [Tuple[Any, Any] or Tuple[Tuple], optional]:
        Limits over which the use of the model is wrong; default valid_range.
        Tuple[Any, Any] in case of scalar value, tuple of tuples in case of vector value.
    - out_of_limits_comment [str, optional]:
        Comment to show in case the value is not valid; default ''
    - distribution [Distribution, optional]:
        Variable random distribution; default None (no distribution)
    - scope [Scope]: {PRIVATE, PROTECTED, PUBLIC},
        Variable visibility; defaults to PRIVATE.
    """

    __slots__ = (
        "_distribution",
        "_limits",
        "_out_of_limits_comment",
        "_valid_range",
        "_invalid_comment",
    )

    def __init__(
        self,
        name: str,
        port: "cosapp.ports.port.BasePort",
        value: Any,
        unit: str = "",
        dtype: Types = None,
        valid_range: RangeValue = None,
        invalid_comment: str = "",
        limits: RangeValue = None,
        out_of_limits_comment: str = "",
        desc: str = "",
        distribution: Optional[Distribution] = None,
        scope: Scope = Scope.PRIVATE,
    ):
        super().__init__(name, port, value, unit, dtype, desc, scope)
        # Additional value check
        value, dtype = self._process_value(value, dtype)

        # TODO: better handle of this possible misunderstanding for users at numpy array instantiation
        if isinstance(value, numpy.ndarray):
            if issubclass(value.dtype.type, numpy.integer):
                logger.warning(
                    f"Variable {name!r} instantiates a numpy array with integer dtype."
                    " This may lead to unpredictible consequences."
                )

        # Check validation ranges are compatible and meaningful for this type of data
        limits, valid_range = self._check_range(limits, valid_range, value)

        if valid_range is None and len(invalid_comment) > 0:
            logger.warning(
                f"Invalid comment specified for variable {name!r} without validity range."
            )
        if limits is None and len(out_of_limits_comment) > 0:
            logger.warning(
                f"Out-of-limits comment specified for variable {name!r} without limits."
            )

        self._valid_range = valid_range  # type: RangeValue
        self._invalid_comment = ""  # type: str
        self.invalid_comment = invalid_comment
        self._limits = limits  # type: RangeValue
        self._out_of_limits_comment = ""  # type: str
        self.out_of_limits_comment = out_of_limits_comment
        self._distribution = None  # type: Optional[Distribution]
        self.distribution = distribution

    @staticmethod
    def _get_limits_from_type(variable: Any) -> RangeValue:
        """Get default limits for a variable depending of its type.

        Parameters
        ----------
        variable : Any
            Variable of interest

        Returns
        -------
        Tuple[float, float] or None
            Default (lower, upper) limits
        """
        if is_numerical(variable):
            return -numpy.inf, numpy.inf
        else:
            return None

    def check_range_type(self, value: Iterable) -> RangeType:
        """Get type of valid_range of limits of variable.
        This function checks if `value` is a size 2 tuple of scalar
        or a tuple of (lower, upper) tuples.
        
        Parameters
        ----------
        value : Any
            value need to be checked

        Returns
        -------
        int (from enum RangeType)
            Type of `value`
        """
        tuple_check = True
        value_check = True

        if isinstance(value, Number):
            raise TypeError(
                "Validity or limit range must be a tuple with format comparable to value"
            )
        if value is not None:
            for bound in value :
                if isinstance(bound, (tuple,list)):
                    value_check = False
                elif isinstance(bound, Number) or bound is None: 
                    tuple_check = False
                else:
                    value_check = False
                    tuple_check = False        
        else :
            return RangeType.NONE
        if value_check and not tuple_check:
            if len(value) != 2:
                raise TypeError(
                    "Valid range or limits must be a size 2 tuple with type comparable to value"
                )
            return RangeType.VALUE
        elif tuple_check and not value_check:
            return RangeType.TUPLE
        else:
            raise ValueError(
                f"Mixed values in valid_range {value} of {self.full_name!r}."
                " Valid object can contain only numerical values or only tuples"
            ) 

    def _check_range(self,
        limits: RangeValue,
        valid_range: RangeValue,
        value: Any,
    ) -> Tuple[RangeValue, RangeValue]:
        """Correct coherence of limits and validation range depending on value type.

        Parameters
        ----------
        limits : Tuple[Any, Any] or Tuple[Tuple] or None
            (lower, upper) limits
        valid_range : Tuple[Any, Any] Tuple[Tuple] or None
            (lower, upper) validation range
        value : Any

        Returns
        -------
        Tuple[Tuple[Any, Any] or Tuple[Tuple] or None, Tuple[Any, Any] or Tuple[Tuple] or None]
            Tuple of corrected (limits, validation range)
        """
        default = Variable._get_limits_from_type(value)
        range_type = self.check_range_type(valid_range)
        limits_type = self.check_range_type(limits)

        if default is not None:

            def get_bounds(lower, upper) -> Tuple[float, float]:
                if lower is None:
                    lower = default[0]
                if upper is None:
                    upper = default[1]
                return (lower, upper) if lower < upper else (upper, lower)

            def raise_inconsistency() -> NoReturn:
                name = self.full_name
                raise ValueError(
                    f"valid_range {valid_range} and limits {limits} of variable {name!r} have different formats"
                )

            if limits is None:
                limits = (None, None)

            if valid_range is None:
                valid_range = limits

            if range_type == RangeType.VALUE:

                min_range, max_range = valid_range = get_bounds(*valid_range)

                if limits_type == RangeType.VALUE:
                    min_limit, max_limit = get_bounds(*limits)
                    limits = (numpy.minimum(min_range, min_limit), numpy.maximum(max_range, max_limit))
                elif limits_type == RangeType.NONE:
                    limits = tuple(default)
                else:
                    raise_inconsistency()

            elif range_type == RangeType.TUPLE:

                valid_range = tuple(get_bounds(*pair) for pair in valid_range)

                if limits_type == RangeType.TUPLE:
                    limits = tuple(get_bounds(*pair) for pair in limits)
                elif limits_type == RangeType.NONE:
                    limits = tuple(default)
                else:
                    raise_inconsistency()
                    
            elif range_type == RangeType.NONE:

                if limits_type == RangeType.VALUE:
                    limits = valid_range = get_bounds(*limits)
                elif limits_type == RangeType.TUPLE:
                    limits = valid_range = tuple(get_bounds(*pair) for pair in limits)
                elif limits_type == RangeType.NONE:
                    limits = valid_range = tuple(default)

        else:
            limits = valid_range = None

        return limits, valid_range

    def _repr_markdown_(self) -> str:
        """Returns the representation of this variable in Markdown format.

        Returns
        -------
        str
            Markdown formatted representation
        """
        msg = {"name":f"**{self.name}**" , "unit": f" {self.unit}" if self.unit else ""}
        value = self.value
        try:
            msg["value"] = f"{value:.5g}"
        except:
            msg["value"] = value

        min_valid, max_valid = (
            self.valid_range if self.valid_range is not None else (None, None)
        )
        min_limit, max_limit = self.limits if self.limits is not None else (None, None)
        
        left_bracket = "&#10647;"
        left_arrow = "&#10205;"
        right_arrow = "&#10206;"
        right_bracket = "&#10648;"
        lock_icon = "&#128274;"
        if min_limit is None or numpy.all(numpy.isinf(min_limit)):
            msg["min_limit"] = ""
        else:
            msg["min_limit"] = f" {left_bracket} {min_limit:.5g} {left_arrow} "
        if max_limit is None or numpy.all(numpy.isinf(max_limit)):
            msg["max_limit"] = ""
        else:
            msg["max_limit"] = f" {right_arrow} {max_limit:.5g} {right_bracket} "
        if min_valid is None or min_limit == min_valid or numpy.all(numpy.isinf(min_valid)):
            msg["min_valid"] = ""
        else:
            msg["min_valid"] = f"{min_valid:.5g} {left_arrow} "
        if max_valid is None or max_limit == max_valid or numpy.all(numpy.isinf(max_valid)):
            msg["max_valid"] = ""
        else:
            msg["max_valid"] = f" {right_arrow} {max_valid:.5g}"
        if self.description:
            msg["description"] = f" | {self.description}"
        else:
            msg["description"] = " |"

        scope_format = {
            Scope.PRIVATE: f" {lock_icon*2} ",
            Scope.PROTECTED: f" {lock_icon} ",
            Scope.PUBLIC: "",
        }
        msg["scope"] = scope_format[self.scope]

        if len(msg["min_limit"] + msg["min_valid"]) == len(msg["max_limit"] + msg["max_valid"]) == 0:
            msg["range"] = ""
            msg["separator"] = ""
        else:
            msg["range"] = " value "
            msg["separator"] = "; "

        return (
            "{name}{scope}: {value!s}{unit}"
            "{separator}{min_limit}{min_valid}{range}{max_valid}{max_limit}"
            "{description}".format(**msg)
        )
    
    def __json__(self) -> Dict[str, Any]:
        """JSONable dictionary representing a variable.
        
        Returns
        -------
        Dict[str, Any]
            The dictionary
        """
        data = super().__json__()
        data.update({
            "valid_range": self.valid_range,
            "invalid_comment": self.invalid_comment,
            "limits": self.limits,
            "out_of_limits_comment": self.out_of_limits_comment,
            "distribution": self.distribution.__json__() if self.distribution else None,
        })
        return data

    @property
    def valid_range(self) -> RangeValue:
        """Tuple[Any, Any] or None : alidity range of the variable and optional comment if unvalid"""
        
        return self._valid_range

    @valid_range.setter
    def valid_range(self, new_range: RangeValue):
        
        range_type = self.check_range_type(new_range)

        value = self.value
        default = self._get_limits_from_type(value)

        if default is not None:
            if range_type == RangeType.VALUE :
                if len(new_range) != 2:
                    raise TypeError(
                        "Validity range must be a size 2 tuple with type comparable to value."
                    )
                limits = self.limits
                valid_range = new_range

            elif range_type == RangeType.TUPLE: 
                limits = self.limits
                valid_range = new_range
                current_range = self.valid_range
                 
            elif range_type == RangeType.NONE:
                limits = self.limits
                valid_range = new_range
                current_range = self.valid_range
                min_valid = (
                    limits[0] if limits[0] > current_range[0] else current_range[0]
                )
                max_valid = (
                    limits[1] if limits[1] < current_range[1] else current_range[1]
                )
                valid_range = (min_valid, max_valid)      
        
        else:
            valid_range = None
            limits = None

        limits, valid_range = self._check_range(self.limits, new_range, value)
        self._valid_range = valid_range
        self._limits = limits

    @property
    def invalid_comment(self) -> str:
        """str : Comment explaining the reasons of the validity range"""
        return self._invalid_comment

    @invalid_comment.setter
    def invalid_comment(self, new_comment: str):
        if not isinstance(new_comment, str):
            raise TypeError(f"invalid_comment must be a string; got {new_comment!s}")
        self._invalid_comment = new_comment

    @property
    def limits(self) -> RangeValue:
        """Tuple[Any, Any] or None : Variable limits and optional comment if unvalid"""
        return self._limits

    @limits.setter
    def limits(self, new_limits: RangeValue):

        limits_type = self.check_range_type(new_limits)

        value = self.value
        default = self._get_limits_from_type(value)

        if default is not None:
            if limits_type == RangeType.VALUE :
                if len(new_limits) != 2:
                    raise TypeError(
                        "Limits must be a size 2 tuple with type comparable to value."
                    )

                limits = new_limits
                if new_limits[0] is None:
                    limits = (default[0], limits[1])
                if new_limits[1] is None:
                    limits = (limits[0], default[1])

                current_range = self.valid_range
                min_valid = max(limits[0], current_range[0])
                max_valid = min(limits[1], current_range[1])
                valid_range = (min_valid, max_valid)
            
            elif limits_type == RangeType.TUPLE:
                limits_list = list(new_limits)
                for index in range(len(limits_list)):

                    if limits_list[index][0] is None:
                       limits_list[index] =  (default[0], limits_list[index][1])
                    if limits_list[index][1] is None:
                       limits_list[index][1] =  (limits_list[index][0],default[1])
                limits = tuple(limits_list)

                current_range = self.valid_range
                valid_range_list = list(current_range)
                for index, valid_range in enumerate(valid_range_list):
                    limit_value = limits[index]
                    range_value = current_range[index]
                    valid_range_list[index] = (max(limit_value[0], range_value[0]), valid_range[1]) 
                    valid_range_list[index] = (valid_range[0], min(limit_value[1], range_value[1]))
                valid_range = tuple(valid_range_list)

            elif limits_type == RangeType.NONE:
                limits = self.limits
                current_range = self.valid_range
                min_valid = max(limits[0], current_range[0])
                max_valid = min(limits[1], current_range[1])
                valid_range = (min_valid, max_valid)


        else:
            limits = valid_range = None

        limits, valid_range = self._check_range(limits, valid_range, value)
        self._valid_range = valid_range
        self._limits = limits

    @property
    def out_of_limits_comment(self) -> str:
        """str : Comment explaining the reasons of the limits"""
        return self._out_of_limits_comment

    @out_of_limits_comment.setter
    def out_of_limits_comment(self, new_comment: str):
        if not isinstance(new_comment, str):
            raise TypeError(f"out_of_limits_comment must be a string; got {new_comment!s}")
        self._out_of_limits_comment = new_comment

    @property
    def distribution(self) -> Optional[Distribution]:
        """Optional[Distribution] : Random distribution of the variable."""
        return self._distribution

    @distribution.setter
    def distribution(self, new_distribution: Optional[Distribution]):
        ok = new_distribution is None or isinstance(new_distribution, Distribution)
        if not ok:
            typename = type(new_distribution).__qualname__
            raise TypeError(
                f"Random distribution should be of type 'Distribution'; got {typename}."
            )
        self._distribution = new_distribution

    def is_valid(self) -> Validity:
        """Get the variable value validity.

        Returns
        -------
        Validity
            Variable value validity
        """
        status = Validity.OK
        value = self.value

        if not isinstance(value, (Number, numpy.ndarray)):
            return status

        if self.valid_range is not None:

            range_type = self.check_range_type(self.valid_range)
            
            if isinstance(value, numpy.ndarray):  
                if range_type == RangeType.VALUE:
                    min_range, max_range = self.valid_range 
                    if numpy.any(value > max_range) or numpy.any(value < min_range):
                        status = Validity.WARNING
                    
                    if self.limits is not None:
                        min_limit, max_limit = self.limits
                        if numpy.any(value > max_limit) or numpy.any(value < min_limit):
                            status = Validity.ERROR

                elif range_type == RangeType.TUPLE:

                    def check_values(bound_list, key) -> None:
                        nonlocal status
                        for v, (lower, upper) in zip(value, bound_list):
                            if not (lower <= v <= upper):
                                status = Validity[key]
                                break

                    check_values(self.valid_range, "WARNING")
                    
                    if self.limits is not None:
                        check_values(self.limits, "ERROR")

                else:
                    varname = f"{self._port.contextual_name}.{self.name}"
                    raise ValueError(
                        f"Mixed values in valid_range {self.valid_range} of {varname!r}."
                        " Valid object can contain only numerical values or only tuples")                     
                
            else:    
                if range_type == RangeType.VALUE:
                    min_range, max_range = self.valid_range          
                    if not min_range <= value <= max_range:
                        status = Validity.WARNING

                        if self.limits is not None:
                            min_limit, max_limit = self.limits
                            if not min_limit <= value <= max_limit:
                                status = Validity.ERROR

                elif range_type == RangeType.TUPLE:
                    varname = f"{self._port.contextual_name}.{self.name}"
                    raise ValueError(
                        f"valid_range {self.valid_range} or limits {self.limits} of variable {varname!r}"
                        f" are incompatible with its value {value}")

        return status

    def get_validity_comment(self, status: Validity) -> str:
        """Get the ground arguments used to established the variable validity range.

        The status `Validity.OK` has no ground arguments.

        Parameters
        ----------
        status : Validity.{OK, WARNING, ERROR}
            Validity status for which the reasons are looked for.

        Returns
        -------
        str
            Validity comment
        """

        def range2str(range: RangeValue) -> str:

            range_type = self.check_range_type(range)

            if range_type == RangeType.VALUE:
                min_valid, max_valid = range if range is not None else (None, None)

            elif range_type == RangeType.TUPLE:
                return f"{range}"[1:-1].join("[]")

            elif range_type == RangeType.NONE:
                min_valid, max_valid = (None, None)


            def get_range_repr(valid, fmt):
                if not isinstance(valid, (list, tuple, numpy.ndarray)):
                    fmt.replace("{}", "{:.5g}")
                return fmt.format(valid)

            if min_valid is None:
                range_repr = "] ,"
            else:
                range_repr = get_range_repr(min_valid, "[{}, ")

            if max_valid is None:
                range_repr += " ["
            else:
                range_repr += get_range_repr(max_valid, "{}]")
            return range_repr

        if status == Validity.ERROR:
            return f"{range2str(self.limits)} - {self.out_of_limits_comment}"
        elif status == Validity.WARNING:
            return f"{range2str(self.valid_range)} - {self.invalid_comment}"
        else:  # Variable is ok
            return ""

    def copy(self, port: "BasePort", name: Optional[str] = None) -> "Variable":
        if name is None:
            name = self.name
        return Variable(
            name,
            value = copy.copy(self.value),
            port = port,
            unit = self._unit,
            dtype = copy.copy(self._dtype),
            valid_range = copy.deepcopy(self._valid_range),
            invalid_comment = self._invalid_comment,
            limits = copy.deepcopy(self._limits),
            out_of_limits_comment = self._out_of_limits_comment,
            desc = self._desc,
            distribution = copy.deepcopy(self._distribution),
            scope = self._scope,
        )

    def _to_raw_dict(self) -> Dict:
        """Convert this variable into a dictionary.
   
        Returns
        -------
        dict
            The dictionary representing this variable.
        """
        data = super()._to_raw_dict()
        data.update({
            "invalid_comment": self.invalid_comment or None,
            "out_of_limits_comment": self.out_of_limits_comment or None,
            "distribution": self.distribution.__json__() if self.distribution else None,
        })
        for key in ["valid_range", "limits"]:
            tmp_val = list(getattr(self, key))
            for idx, val in enumerate(tmp_val):
                if numpy.isinf(val):
                    tmp_val[idx] = str(val) 
            if  tmp_val == ["-inf", "inf"]:
                tmp_val = None
            data[key] = tmp_val 
        
        return data
