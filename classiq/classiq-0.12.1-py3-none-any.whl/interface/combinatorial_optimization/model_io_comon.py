#################################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES), and is copyright (c) 2018-2021
# by the software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia University
# Research Corporation, et al.  All rights reserved.
#
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and
# license information.
#################################################################################
"""
Functions for saving and loading Pyomo objects to json
"""


# TODO: Make this file clearer: better naming, type hints.
# See: https://classiq.atlassian.net/browse/CAD-568

from typing import Any, List, Tuple

import pyomo
import pyomo.core.base
import pyomo.core.expr
from pyomo.core.base.indexed_component import IndexedComponent
from pyomo.environ import (
    Component,
    Expression,
    ExternalFunction,
    Param,
    RangeSet,
    Suffix,
    Var,
    value,
)
from pyomo.network import Port


def may_have_subcomponents(obj) -> bool:
    return callable(getattr(obj, "component_objects", None))


def _set_active(obj: Any, attr_value: Any) -> None:
    """
    Set if component is active, used for read active attribute callback.
    Args:
        obj: object whose attribute is to be set
        attr_value: attribute value
    Returns:
        None
    """

    def change_active_attr(_obj: Any, active: Any) -> None:
        if hasattr(_obj, "_active"):
            _obj._active = active

    change_active_attr(obj, attr_value)
    if hasattr(obj, "_component") and obj._component is not None:
        change_active_attr(obj._component, attr_value)


def _set_sense(obj, attr_value):
    """
    Set if component is minimize or maximize.
    Args:
        obj: object whose attribute is to be set
        attr_value: attribute value
    Returns:
        None
    """
    obj._sense = attr_value
    obj._init_sense = attr_value


def _set_fixed(obj, attr_value):
    """
    Set if variable is fixed, used for read fixed attribute callback.
    Args:
        obj: object whose attribute is to be set
        attr_value: attribute value
    Returns:
        None
    """
    if attr_value:
        obj.fix()
    else:
        obj.unfix()


def _get_value(obj):
    """
    Get object value attribute callback.
    Args:
        obj: object whose attribute is to be set
    Returns:
        value
    """
    return value(obj, exception=False)


def _get_strict(obj):
    """
    Get object strict attribute callback.
    Args:
        obj: object
    Returns:
        strict value
    """
    return obj._strict


def _get_domain(obj):
    """
    Get object domain attribute callback.
    Args:
        obj: object
    Returns:
        domain string value
    """
    return obj.domain.name


def _get_index_name(obj: IndexedComponent) -> str:
    return obj.index_set().name


def _set_value(obj, attr_value):
    """
    Set object value attribute callback. We change even not  mutable objects.
    Args:
        obj: object whose attribute is to be set
        attr_value: attribute value
    Returns:
        None
    """
    try:
        obj.value = attr_value
    except AttributeError:
        pass


def _set_lb(obj, attr_value):
    """
    Set variable lower bound, used for read lb attribute callback.
    Args:
        obj: object whose attribute is to be set
        attr_value: attribute value
    Returns:
        None
    """
    obj.setlb(attr_value)


def _set_ub(obj, attr_value):
    """
    Set variable upper bound, use for read ub attribute callback.
    Args:
        obj: object whose attribute is to be set
        attr_value: attribute value
    Returns:
        None
    """
    obj.setub(attr_value)


def _set_strict(obj, attr_value):
    """
    Set variable strict attribute.
    Args:
        obj: object whose attribute is to be set
        attr_value: attribute value
    Returns:
        None
    """
    obj._strict = attr_value


def _only_fixed(obj, attrs):
    """
    Returns a list of attributes to read for a variable, only whether it is
    fixed for non-fixed variables and if it is fixed and the value for fixed
    variables.  The allows you to set up a serializer that only reads fixed
    variable values.
    Args:
        obj: Pyomo component being loaded
        attrs: State dictionary for the component obj.
    Returns:
        An attribute list to read. Loads fixed for either fixed or un-fixed
        variables, but only reads in values for unfixed variables.  This is
        useful for initialization functions.
    """
    if attrs["fixed"]:
        return "value", "fixed"
    else:
        return ("fixed",)


class StoreSpec(object):
    """
    A StoreSpec object tells the serializer functions what to read or write.
    The default settings will produce a StoreSpec configured to load/save the
    typical attributes required to load/save a model state.
    Args:
        classes: A list of classes to save.  Each class is represented by a
            list (or tuple) containing the following elements: (1) class
            (compared using isinstance) (2) attribute list or None, an empty
            list store the object, but none of its attributes, None will not
            store objects of this class type (3) optional load filter function.
            The load filter function returns a list of attributes to read based
            on the state of an object and its saved state. The allows, for
            example, loading values for unfixed variables, or only loading
            values whose current value is less than one. The filter function
            only applies to load not save. Filter functions take two arguments
            (a) the object (current state) and (b) the dictionary containing the
            saved state of an object.  More specific classes should come before
            more general classes.  For example if an object is a HeatExchanger
            and a UnitModel, and HeatExchanger is listed first, it will follow
            the HeatExchanger settings.  If UnitModel is listed first in the
            classes list, it will follow the UnitModel settings.
        data_classes: This takes the same form as the classes argument.
            This is for component data classes.
        skip_classes: This is a list of classes to skip.  If a class appears
            in the skip list, but also appears in the classes argument, the
            classes argument will override skip_classes. The use for this is to
            specifically exclude certain classes that would get caught by more
            general classes (e.g. UnitModel is in the class list, but you want
            to exclude HeatExchanger which is derived from UnitModel).
        ignore_missing: If True will ignore a component or attribute that exists
            in the model, but not in the stored state. If false an exception
            will be raised for things in the model that should be loaded but
            aren't in the stored state. Extra items in the stored state will not
            raise an exception regardless of this argument.
        suffix: If True store suffixes and component ids.  If false, don't store
            suffixes.
        suffix_filter: None to store all suffixes if suffix=True, or a list of
            suffixes to store if suffix=True
    """

    def __init__(
        self,
        classes=(
            (Param, ("_mutable",)),
            (Var, ()),
            (Expression, ()),
            (Component, ("active",)),
            (pyomo.core.base.objective.Objective, ("sense",)),
            (pyomo.core.base.indexed_component.IndexedComponent, ("index",)),
        ),
        data_classes=(
            (
                pyomo.core.base.var._VarData,
                ("fixed", "stale", "value", "lb", "ub", "domain"),
            ),
            (pyomo.core.base.param._ParamData, ("value",)),
            (int, ("value",)),
            (float, ("value",)),
            (pyomo.core.base.expression._ExpressionData, ()),
            (pyomo.core.base.component.ComponentData, ("active",)),
            (pyomo.core.base.constraint._GeneralConstraintData, ()),
            (pyomo.core.expr.numvalue.NumericConstant, ("value",)),
            (pyomo.core.expr.logical_expr.InequalityExpression, ("strict",)),
            (pyomo.core.base.objective.ScalarObjective, ("sense",)),
            (pyomo.core.base.set.RangeSet, ("_init_data",)),
        ),
        skip_classes=(ExternalFunction, Port, Expression, RangeSet),
        ignore_missing=True,
        suffix=True,
        suffix_filter=None,
    ) -> None:
        """
        (see above)
        """
        # Callbacks are used for attributes that cannot be directly get or set
        self.get_functions = {
            "value": _get_value,
            "strict": _get_strict,
            "domain": _get_domain,
            "index": _get_index_name,
        }
        self.set_functions = {
            "_mutable": lambda *args: None,
            "active": _set_active,
            "fixed": _set_fixed,
            "lb": _set_lb,
            "ub": _set_ub,
            "value": _set_value,
            "strict": _set_strict,
            "sense": _set_sense,
        }

        skip_with_classes: List[Any] = [
            (i, []) for i in skip_classes if i not in classes
        ] + list(classes)
        self.classes = [i[0] for i in skip_with_classes]
        # Add skip classes to classes list, with None as attr list to skip
        self.class_attrs = [i[1] for i in skip_with_classes]
        self.data_classes = [i[0] for i in data_classes]
        self.data_class_attrs = [i[1] for i in data_classes]
        # Create filter function lists, use None if not supplied
        self.class_filter = [i[2] if len(i) > 2 else None for i in skip_with_classes]
        self.data_class_filter = [i[2] if len(i) > 2 else None for i in data_classes]
        self.ignore_missing = ignore_missing
        self.include_suffix = suffix
        self.suffix_filter = suffix_filter

    def set_read_callback(self, attr, cb=None):
        """
        Set a callback to set an attribute, when reading from json or dict.
        """
        self.set_functions[attr] = cb

    def set_write_callback(self, attr, cb=None):
        """
        Set a callback to get an attribute, when writing to json or dict.
        """
        self.get_functions[attr] = cb

    def get_class_attr_list(self, obj) -> Tuple[List[Any], Any]:
        """
        Look up what attributes to save/load for an Component object.
        Args:
            obj: Object to look up attribute list for.
        Return:
            A list of attributes and a filter function for object type
        """
        attr_list = []  # Attributes to store
        filter_function = None  # Load filter function
        for i, cl in enumerate(self.classes):
            if isinstance(obj, cl) or (isinstance(obj, type) and issubclass(obj, cl)):
                attr_list += list(self.class_attrs[i])
                filter_function = self.class_filter[i]  # this does not make sense
        return attr_list, filter_function

    def get_data_class_attr_list(self, obj) -> Tuple[List[Any], Any]:
        """
        Look up what attributes to save/load for an ComponentData object.
        Args:
            obj: Object or type to look up attribute list for.
        Return:
            A list of attributes and a filter function for object type
        """
        attr_list = []  # Attributes to store
        filter_function = None  # Load filter function
        for i, cl in enumerate(self.data_classes):
            if isinstance(obj, cl) or (isinstance(obj, type) and issubclass(obj, cl)):
                attr_list += list(self.data_class_attrs[i])
                filter_function = self.data_class_filter[
                    i
                ]  # TODO: this does not make sense
        return attr_list, filter_function

    @classmethod
    def bound(cls):
        """Returns a StoreSpec object to store variable bounds only."""
        return cls(
            classes=((Var, ()),),
            data_classes=((pyomo.core.base.var._VarData, ("lb", "ub")),),
            suffix=False,
        )

    @classmethod
    def value(cls):
        """Returns a StoreSpec object to store variable values only."""
        return cls(
            classes=((Var, ()),),
            data_classes=((pyomo.core.base.var._VarData, ("value",)),),
            suffix=False,
        )

    @classmethod
    def isfixed(cls):
        """Returns a StoreSpec object to store if variables are fixed."""
        return cls(
            classes=((Var, ()),),
            data_classes=((pyomo.core.base.var._VarData, ("fixed",)),),
            suffix=False,
        )

    @classmethod
    def suffix(cls, suffix_filter=None):
        return cls(
            classes=((Suffix, ()),),
            data_classes=(),
            suffix=True,
            suffix_filter=suffix_filter,
        )

    @classmethod
    def value_isfixed(cls, only_fixed):
        """
        Return a StoreSpec object to store variable values and if fixed.
        Args:
            only_fixed: Only load fixed variable values
        """
        if only_fixed:
            return cls(
                classes=((Var, ()),),
                data_classes=(
                    (pyomo.core.base.var._VarData, ("value", "fixed"), _only_fixed),
                ),
                suffix=False,
            )
        else:
            return cls(
                classes=((Var, ()),),
                data_classes=((pyomo.core.base.var._VarData, ("value", "fixed")),),
                suffix=False,
            )

    @classmethod
    def value_isfixed_isactive(cls, only_fixed):
        """
        Return a StoreSpec object to store variable values, if variables are
        fixed and if components are active.
        Args:
            only_fixed: Only load fixed variable values
        """
        if only_fixed:
            return cls(
                classes=((Var, ()), (Param, ()), (Component, ("active",))),
                data_classes=(
                    (pyomo.core.base.var._VarData, ("value", "fixed"), _only_fixed),
                    (pyomo.core.base.param._ParamData, ("value",)),
                    (pyomo.core.base.component.ComponentData, ("active",)),
                ),
                suffix=False,
            )
        else:
            return cls(
                classes=((Var, ()), (Param, ()), (Component, ("active",))),
                data_classes=(
                    (pyomo.core.base.var._VarData, ("value", "fixed")),
                    (pyomo.core.base.param._ParamData, ("value",)),
                    (pyomo.core.base.component.ComponentData, ("active",)),
                ),
                suffix=False,
            )
