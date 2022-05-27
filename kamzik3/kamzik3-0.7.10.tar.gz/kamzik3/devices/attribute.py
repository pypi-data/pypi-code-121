import math
from time import perf_counter_ns
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, KeysView

import pint
from pint import Quantity

from numpy import (
    dtype,
    float16,
    float32,
    float64,
    uint16,
    uint32,
    uint64,
    int16,
    int32,
    int64,
    uint8,
    int8,
    ndarray,
)

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.constants import SAVE_CHANGE
from kamzik3.snippets.snippetDataAccess import is_equal

PINT_ERRORS = (
    pint.UndefinedUnitError,
    pint.DefinitionSyntaxError,
    AttributeError,
)


class SetFunction:
    """
    Decorator for setting Attributes value.

    Used when attribute value is not set directly, but via set function.
    """

    def __init__(self, attribute, callback=None):
        """
        Initiate for which attribute we need to setup flag and callback.

        :param Attribute attribute: Desired Attribute
        :param Callable callback: Callback after value was set
        """
        self.attribute = attribute
        self.callback = callback

    def __enter__(self):
        """
        Set flag and callback for desired Attribute.

        :return Attribute
        """
        self.attribute.with_set_function = True
        self.attribute.set_callback = self.callback
        return self.attribute

    def __exit__(self, value_type, value, traceback):
        """
        Clear set_function and callback after value was set.

        :param value_type:
        :param value:
        :param traceback:
        """
        self.attribute.with_set_function = False
        self.attribute.set_callback = None


class Attribute(dict):
    """
    Class definition of Attribute.

    Attribute extends Dictionary with predefined and user defined keys.

    Predefined keys are:

        VALUE: value of the attribute (value of specified type)
        TYPE: type of the attribute (int, float, ...)
        UNIT: desired unit of Attributes values (mm, degC, degK, ...)
        READONLY: value is readonly for Client
        DESCRIPTION: short description of Attributes purpose / meaning
        SETPOINT: when using setFunction, SETPOINT is first set
        SAVE_CHANGES: when set to True, after value is set, it's also written and save
        in the config file
        ALLOW_BROADCAST: allow broadcasting changes of Attribute to Client
        PREVIOUS: previous VALUE of Attribute after new VALUE was set

    Numerical Type keys:

        OFFSET: value offset (value + offset)
        FACTOR: value factor (value * factor)
        DECIMALS: specify number of decimals after decimal point
        MIN: minimum allowed value
        MAX: maximum allowed value
        TOLERANCE: tuple of (negative, positive) tolerance.
                   It's use to determine if value is set within specified tolerances.
    """

    # Holds main attributes, which each dict has to contain in order to be convertible
    # into Attribute
    attribute_keys = {VALUE, TYPE, UNIT, READONLY, DESCRIPTION}
    integer_types = (int8, int16, int32, int64, uint8, uint16, uint32, uint64)
    float_types = (float16, float32, float64)
    unsigned_types = (uint8, uint16, uint32, uint64)
    # Helper flag for SetFunction decorator
    with_set_function = False
    # Holds last time, that Attribute value was streamed to clients
    last_broadcast_time = last_update_time = perf_counter_ns()
    # Holds diff between last_stream_time and current time
    last_update_time_diff = 0
    # Indicates if attribute is numerical. It's set automatically based on TYPE.
    numerical = False
    # Token identifier associate with setting of new value
    set_token = 0
    # Any callable function to call after value was set
    set_callback = None
    # Minimum time in between of value change stream.
    # Every Attribute change between 0 and min_broadcast_timeout would not be broadcast
    # to the client.
    # Set this attribute to zero to stream every change.
    # Default value is in nanoseconds (100ms)
    min_broadcast_timeout = 0 * 1e6

    def __init__(
        self,
        attribute_id=None,
        default_value=None,
        min_value=None,
        max_value=None,
        unit: Optional[str] = None,
        set_function=None,
        default_type="str",
        decimals=0,
        readonly=False,
        description=None,
        set_value_when_set_function=True,
        tolerance=(0, 0),
        factor=1,
        offset=0,
        save_change=False,
        allow_broadcast=True,
        **kwargs
    ):
        """
        Initiate new Attribute object.

        When using with Device, always use device.create_attribute method.

        :param str attribute_id: Attribute id, it must be unique in context of one
         Device
        :param mixed default_value: Default VALUE
        :param float min_value: MIN value, ignored for str TYPE.
         Means inf if None for Numerical value.
        :param float max_value: MAX value, ignored for str TYPE.
         Means inf if None for Numerical value.
        :param str unit: Main UNIT of the attribute
        :param Callable set_function: Function to call when setting the VALUE
        :param str default_type: Default TYPE
        :param uint decimals: Number of DECIMALS after decimal point
        :param bool readonly: Specify if Attribute is READONLY for client
        :param str description: Short DESCRIPTION
        :param bool set_value_when_set_function: Set VALUE at the same time as calling
         the set_function
        :param list tolerance: (negative tolerance, positive tolerance)
        :param float factor: FACTOR to multiply with VALUE
        :param float offset: OFFSET to add to VALUE
        :param bool save_change: Save VALUE into config file as well
        :param bool allow_broadcast: Allow broadcast VALUE change to the client
        :param dict kwargs: User defined keys
        """
        dict.__init__(self)
        self._callbacks: Dict[Callable, List] = {}
        self.attribute_id = attribute_id
        self.set_function = set_function
        self.default_type = default_type

        self[OFFSET] = offset
        self[FACTOR] = factor
        # Set attribute value flag when using set function.
        # This flag prevents change of Attribute's value before value is actually
        # set on device side.
        self.set_value_when_set_function = set_value_when_set_function
        if unit is None:
            unit = ""
        self[UNIT] = unit
        self.min_broadcast_timeout = kwargs.get("min_broadcast_timeout", 0) * 1e6
        default_type = kwargs.get(TYPE, default_type)
        if default_type == TYPE_LIST:
            # Special type LIST
            self[TYPE] = TYPE_LIST
        elif isinstance(default_type, (list, KeysView)):
            #  Used for Combox implementation
            self[TYPE] = TYPE_LIST
            self[TYPE_LIST_VALUES] = list(default_type)
        elif default_type == TYPE_ARRAY or isinstance(default_type, ndarray):
            # Special type Array
            self[TYPE] = TYPE_ARRAY
        else:
            # Default TYPE is either string or Numerical
            default_type = dtype(default_type)
            self[TYPE] = dtype(default_type).name
            if default_type in self.integer_types:
                self[DECIMALS] = 0
                if min_value is None and default_type in self.unsigned_types:
                    self[MIN] = 0
                else:
                    self[MIN] = int(min_value) if min_value is not None else -math.inf
                self[MAX] = int(max_value) if max_value is not None else math.inf
                self.numerical = True
            elif default_type in self.float_types:
                self[DECIMALS] = decimals
                self[MIN] = float(min_value) if min_value is not None else -math.inf
                self[MAX] = float(max_value) if max_value is not None else math.inf
                self.numerical = True
        if self.numerical:
            self[TOLERANCE] = [float(tolerance[0]), float(tolerance[1])]
        self[READONLY] = readonly
        self[DESCRIPTION] = description
        self[VALUE] = default_value
        self[SETPOINT] = None
        self[PREVIOUS] = None
        self[SAVE_CHANGE] = save_change
        self[ALLOW_BROADCAST] = allow_broadcast

        # Update Dict with user defined key -> value pairs
        self.update(kwargs)

    def _update_set_time(self):
        """Set last_update_time and last_update_time_diff for future reference."""
        update_time = perf_counter_ns()
        self.last_update_time_diff = update_time - self.last_update_time
        self.last_update_time = update_time

    def allow_broadcast(self) -> bool:
        """
        Allow broadcast VALUE change.

        if ALLOW_BROADCASt is True and broadcast_timeout was exceeded

        :return: bool
        """
        return (
            self[ALLOW_BROADCAST]
            and (perf_counter_ns() - self.last_broadcast_time)
            >= self.min_broadcast_timeout
        )

    def __setitem__(self, k, v):
        """
        Called when value of the key is changed.

        :param str k: dict key
        :param mixed v: key value
        """
        if k == VALUE:
            self._update_set_time()
            try:
                self[PREVIOUS] = self[VALUE]
            except KeyError:
                pass
            if isinstance(v, Quantity):
                try:
                    v = v.to(self[UNIT]).m
                except AttributeError:
                    v = v.m
        elif k == TOLERANCE:
            # Make sure, that tolerance is of float type
            v = [float(t) for t in v]
        elif k == UNIT and v is not None:
            if v == "%":
                # We have to treat percent sign and turn in into 'percent' value
                v = "percent"
            if v not in ("", None):
                # Unit does not exists in pint units dictionary
                if units.parse_unit_name(v) == ():
                    # We define that new unit quantity equals 1
                    units.define("{}=1".format(v))
                    units.derived_units.append(v)
        try:
            # Return, if current and new value is equal
            if is_equal(self[k], v):
                return
        except KeyError:
            pass

        # We want to set VALUE using set_function
        if k == VALUE and self.set_function and self.with_set_function:
            self[SETPOINT] = v
            setpoint = self.remove_offset_factor(v)
            # Release set function flag
            self.with_set_function = False
            if self.set_value_when_set_function:
                # Store actual attribute[k] value into dictionary
                super().__setitem__(k, v)
            # Call set function
            if hasattr(self.set_function, "callback"):
                self.set_token = self.set_function(setpoint, callback=self.set_callback)
            else:
                # We don't have callback in a function, so just call it
                self.set_token = self.set_function(setpoint)
            if not self.set_value_when_set_function:
                return
        else:
            # Store actual attribute[k] value into dictionary
            super().__setitem__(k, v)

        self.handle_callbacks(k, v)

    def handle_callbacks(self, k, v):
        """
        Here comes a short description of handle_callbacks.

        When any parameter of attribute is set, call all relevant callbacks that are
        attached to the parameter.

        :param k: attribute key
        :type k: hashable
        :param v: attribute value
        :type v: object
        """
        # Call all relevant callbacks
        for (
            callback,
            (
                max_update_rate,
                updated_at,
                key_filter,
            ),
        ) in self._callbacks.copy().items():
            # Check update rate, continue if it's less than max_update_rate
            if (
                k == VALUE
                and max_update_rate is not None
                and (self.last_update_time - updated_at) <= max_update_rate
            ):
                continue
            # Check if key_filter is set
            if key_filter is None:
                # Key can be any value, therefore callback with key and value
                callback(k, v)
            elif k == key_filter:
                # Since we have filter set, callback with just value
                callback(v)
            else:
                continue
            try:
                # Set last callback time
                self._callbacks[callback][1] = perf_counter_ns()
            except KeyError:
                # Callback no longer exists, skipping
                pass

    def attribute_copy(self):
        """
        Create copy of Attribute.

        :return Attribute: Copy of this Attribute
        """
        return Attribute(**self)

    @staticmethod
    def from_dict(dictionary: Union[Dict[str, Any], Any]) -> Union["Attribute", Any]:
        """
        Create Attribute from input dictionary (recursively).

        Check if input dictionary can be converted into Attribute.

        :param dict dictionary: Input dictionary
        :return Attribute: Attribute if convertible
        """
        if isinstance(dictionary, dict):
            if Attribute.is_attribute(dictionary):
                # Check if unit is valid, if not add it's definition to Pint
                if dictionary[UNIT] not in ("", None):
                    try:
                        units.get_name(dictionary[UNIT])
                    except pint.errors.UndefinedUnitError:
                        units.define("{}=1".format(dictionary[UNIT]))
                        units.derived_units.append(dictionary[UNIT])
                return Attribute(**dictionary)
            else:
                for key, attribute in dictionary.items():
                    dictionary[key] = Attribute.from_dict(attribute)
            return dictionary
        else:
            return dictionary

    @staticmethod
    def is_attribute(dictionary) -> bool:
        """
        Check if provided dictionary is convertible to Attribute.

        Attribute.attribute_keys must be subset of Input dictionary keys.

        :param dict dictionary: Input dictionary
        :return: bool
        """
        try:
            return Attribute.attribute_keys.issubset(dictionary.keys())
        except (AttributeError, TypeError, ValueError):
            return False

    def attach_callback(
        self,
        callback: Callable,
        max_update_rate: Optional[float] = None,
        key_filter: Optional[str] = None,
    ):
        """
        Attach callback to Attribute.

        :param Callable callback: callable function
        :param float max_update_rate: max update rate in ms
        :param str key_filter:
        """
        assert callable(callback)

        if callback not in self._callbacks:
            if max_update_rate is not None:
                # Convert rate to nanoseconds
                max_update_rate *= 1e6
            self._callbacks[callback] = [max_update_rate, perf_counter_ns(), key_filter]

    def detach_callback(self, callback):
        """
        Detach callback from attribute.

        :param Callable callback: callable function
        """
        assert callable(callback)
        try:
            del self._callbacks[callback]
        except KeyError:
            pass  # Callback no longer exists

    def apply_offset_factor(self, value=None):
        """
        Apply offset and factor to attribute value.

        :param value: numerical value
        :return: mixed
        """
        if value is None:
            value = self[VALUE]

        if value is not None and self.numerical:
            return (value + self[OFFSET]) * self[FACTOR]
        elif self.default_type is bool:
            return self[FACTOR] == value
        else:
            return value

    def remove_offset_factor(self, value=None):
        """
        Remove offset and factor from attribute value.

        :param value: numerical value
        :return: mixed
        """
        if value is None:
            value = self[VALUE]
        if value is not None and self.numerical:
            return (value / self[FACTOR]) - self[OFFSET]
        elif self.default_type is bool:
            return self[FACTOR] == value
        else:
            return value

    def read_and_reset_token(self) -> int:
        """
        Return token and reset it back to 0.

        :return: int
        """
        token = self.set_token
        self.set_token = 0
        return token

    @staticmethod
    def list_attribute(attribute: Union[str, List, Tuple]) -> List:
        """
        Create list from input attribute.

        :param attribute: mixed
        :return: list
        """
        if isinstance(attribute, list):
            return attribute
        elif isinstance(attribute, tuple):
            return list(attribute)
        else:
            return [attribute]

    def convert_units(self, value: Quantity):
        """
        Convert input value to current attribute unit.

        :param Quantity value: Quantity
        :return: value or Quantity
        """
        assert isinstance(value, Quantity)
        if value.dimensionless:
            if self[UNIT] is None:
                return value
            else:
                return units.Quantity("{} {}".format(value.m, self[UNIT]))

        return value.to(self[UNIT])

    def within_limits(self, value: Quantity) -> bool:
        """
        Check if value is within limits.

        MIN <= VALUE <= MAX

        :param Quantity value:  Quantity
        :return: bool
        """
        assert isinstance(value, Quantity)
        return bool(self.minimum() <= value <= self.maximum())

    def within_tolerance(self, value: Quantity) -> bool:
        """
        Check if value is within tolerance.

        :param Quantity value:  Value to check
        :return: bool
        """
        assert isinstance(value, Quantity)
        setpoint = self.setpoint()
        if setpoint is None:
            setpoint = self.value()
        return bool(
            (setpoint - self.negative_tolerance())
            <= value
            <= (setpoint + self.positive_tolerance())
        )

    def value(self):
        """
        Get Attribute's value.

        :return: a Quantity or the non-numerical value of the attribute
        """
        if self.numerical:
            try:
                return units.Quantity(self[VALUE], self[UNIT])
            except PINT_ERRORS:
                return units.Quantity(self[VALUE])
            except TypeError:
                return self[VALUE]
        else:
            return self[VALUE]

    def minimum(self):
        """
        Get Attribute's minimum value.

        :return: a Quantity or the non-numerical value of the attribute's minimum
        """
        if self.numerical:
            try:
                return units.Quantity(self[MIN], self[UNIT])
            except PINT_ERRORS:
                return units.Quantity(self[MIN])
            except TypeError:
                return self[MIN]
        else:
            return self[MIN]

    def maximum(self):
        """
        Get Attribute's maximum value.

        :return: a Quantity or the non-numerical value of the attribute's maximum
        """
        if self.numerical:
            try:
                return units.Quantity(self[MAX], self[UNIT])
            except PINT_ERRORS:
                return units.Quantity(self[MAX])
            except TypeError:
                return self[MAX]
        else:
            return self[MAX]

    def negative_tolerance(self):
        """
        Get Attribute's negative tolerance.

        :return: a Quantity or the non-numerical value of the attribute's negative
         tolerance
        """
        if self.numerical:
            try:
                return units.Quantity(self[TOLERANCE][0], self[UNIT])
            except PINT_ERRORS:
                return units.Quantity(self[TOLERANCE][0])
            except TypeError:
                return self[TOLERANCE][0]
        else:
            return self[TOLERANCE][0]

    def positive_tolerance(self):
        """
        Get Attribute's positive tolerance.

        :return: a Quantity or the non-numerical value of the attribute's positive
         tolerance
        """
        if self.numerical:
            try:
                return units.Quantity(self[TOLERANCE][1], self[UNIT])
            except PINT_ERRORS:
                return units.Quantity(self[TOLERANCE][1])
            except TypeError:
                return self[TOLERANCE][1]
        else:
            return self[TOLERANCE][1]

    def offset(self):
        """
        Get Attribute's value offset.

        :return: a Quantity or the non-numerical value of the attribute's offset
        """
        if self.numerical:
            try:
                return units.Quantity(self[OFFSET], self[UNIT])
            except PINT_ERRORS:
                return units.Quantity(self[OFFSET])
            except TypeError:
                return self[OFFSET]
        else:
            return self[OFFSET]

    def setpoint(self):
        """
        Get Attribute's setpoint.

        :return: a Quantity or the non-numerical value of the attribute's setpoint
        """
        if self.numerical:
            try:
                return units.Quantity(self[SETPOINT], self[UNIT])
            except PINT_ERRORS:
                return units.Quantity(self[SETPOINT])
            except TypeError:
                return self[SETPOINT]
        else:
            return self[SETPOINT]

    def unit(self) -> Any:
        """
        Get Attribute's unit.

        :return: str
        """
        return self[UNIT]
