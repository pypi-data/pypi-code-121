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
Functions for loading Pyomo objects from json
"""

# TODO: Make this file clearer: better naming, type hints.
# See: https://classiq.atlassian.net/browse/CAD-568

import ast
import gzip
import inspect
import json
import time
import weakref
from typing import Any, Dict, Optional, Tuple

import pyomo.core.base
import pyomo.core.expr.numeric_expr
from pyomo.environ import Objective, RangeSet, Set, Suffix

from classiq.interface.combinatorial_optimization.model_io_comon import (
    StoreSpec,
    may_have_subcomponents,
)
from classiq.interface.pyomo_extension import pyomo

__format_version__ = 1

PyomoObject = Dict  # TODO this probably fits json versions, but generally unrecommended


def get_last_object_from_lookup(lookup, object_name) -> Optional[object]:
    for object_lookup in reversed(lookup.values()):
        if hasattr(object_lookup, "name") and object_name == object_lookup.name:
            return object_lookup
    return None


PYOMO_CLASS_MAPPING = {
    "<class 'pyomo.core.base.PyomoModel.ConcreteModel'>": pyomo.core.base.PyomoModel.ConcreteModel,
    "<class 'pyomo.core.base.param.ScalarParam'>": pyomo.core.base.param.ScalarParam,
    "<class 'pyomo.core.base.var.IndexedVar'>": pyomo.core.base.var.IndexedVar,
    "<class 'pyomo.core.base.var._GeneralVarData'>": pyomo.core.base.var._GeneralVarData,
    "<class 'pyomo.core.base.logical_constraint.IndexedLogicalConstraint'>": pyomo.core.base.logical_constraint.IndexedLogicalConstraint,
    "<class 'pyomo.core.base.logical_constraint._GeneralLogicalConstraintData'>": pyomo.core.base.logical_constraint._GeneralLogicalConstraintData,
    "<class 'pyomo.core.base.constraint.IndexedConstraint'>": pyomo.core.base.constraint.IndexedConstraint,
    "<class 'pyomo.core.base.constraint._GeneralConstraintData'>": pyomo.core.base.constraint._GeneralConstraintData,
    "<class 'pyomo.core.base.constraint.ScalarConstraint'>": pyomo.core.base.constraint.ScalarConstraint,
    "<class 'pyomo.core.expr.numvalue.NumericConstant'>": pyomo.core.expr.numvalue.NumericConstant,
    "<class 'pyomo.core.base.objective.ScalarObjective'>": pyomo.core.base.objective.ScalarObjective,
    "<class 'pyomo.core.expr.numeric_expr.SumExpression'>": pyomo.core.expr.numeric_expr.SumExpression,
    "<class 'pyomo.core.expr.numeric_expr.ProductExpression'>": pyomo.core.expr.numeric_expr.ProductExpression,
    "<class 'pyomo.core.expr.logical_expr.InequalityExpression'>": pyomo.core.expr.logical_expr.InequalityExpression,
    "<class 'pyomo.core.expr.logical_expr.EqualityExpression'>": pyomo.core.expr.logical_expr.EqualityExpression,
    "<class 'pyomo.core.base.set.OrderedScalarSet'>": pyomo.core.base.set.OrderedScalarSet,
    "<class 'pyomo.core.base.set.FiniteScalarRangeSet'>": pyomo.core.base.set.FiniteScalarRangeSet,
    "<class 'pyomo.core.expr.numeric_expr.MonomialTermExpression'>": pyomo.core.expr.numeric_expr.MonomialTermExpression,
    "<class 'pyomo.core.base.set.FiniteScalarSet'>": pyomo.core.base.set.FiniteScalarSet,
    "<class 'pyomo.core.expr.numeric_expr.NegationExpression'>": pyomo.core.expr.numeric_expr.NegationExpression,
    "<class 'pyomo.core.expr.numeric_expr.PowExpression'>": pyomo.core.expr.numeric_expr.PowExpression,
    "<class 'float'>": float,
    "<class 'int'>": int,
    "<class 'tuple'>": tuple,
    "<class 'str'>": str,
}


def _read_component(
    obj_dict: Dict[Optional[str], Dict[str, Any]],
    store_spec: StoreSpec,
    lookup: Dict[int, PyomoObject],
    suffixes: Dict[int, Dict[str, int]],
    root_name: Optional[str] = None,
):
    """
    Read a component dictionary into a model
    """

    try:
        root_dict = obj_dict[root_name]
    except KeyError as e:
        if store_spec.ignore_missing:
            return
        else:
            raise e

    # read sub data and overwrite
    components_dict = _read_component_data(
        root_dict["data"], store_spec, lookup=lookup, suffixes=suffixes
    )
    for object_name in components_dict.keys():
        object_lookup = get_last_object_from_lookup(
            lookup=lookup, object_name=root_name
        )
        if object_lookup is not None:
            components_dict[object_name] = object_lookup

    # create obj from dict
    pyomo_class = PYOMO_CLASS_MAPPING[root_dict["__type__"]]
    if issubclass(pyomo_class, Set):
        obj = pyomo_class(
            initialize=[ast.literal_eval(arg) for arg in root_dict["data"]]
        )
    elif len(components_dict) == 1 and None in components_dict:
        obj = list(components_dict.values())[0]
        if hasattr(obj, "construct") and isinstance(obj, RangeSet):
            obj._constructed = False
            obj.construct()
    else:
        args_parsed = get_last_object_from_lookup(
            lookup, object_name=root_dict.get("index", None)
        )
        obj = pyomo_class(args_parsed)
        if hasattr(obj, "construct"):
            obj.construct()

        for key, el in components_dict.items():
            el._component = weakref.ref(obj)
            obj._data[key] = el

    # set attributes to obj
    attr_list, filter_function = store_spec.get_class_attr_list(pyomo_class)
    if filter_function is not None:
        attr_list = filter_function(obj, root_dict)
    obj = _set_attributes_from_dict(obj, root_dict, attr_list, store_spec)

    # make a dict of suffixes to read at the end
    if isinstance(obj, Suffix):
        if store_spec.include_suffix:
            if (
                store_spec.suffix_filter is None
                or root_name in store_spec.suffix_filter
            ):
                suffixes[root_dict["__id__"]] = root_dict["data"]  # is populated

    lookup[root_dict["__id__"]] = obj
    return obj


def _read_component_data(
    obj_dict: Dict[str, Dict[str, Any]],
    store_spec: StoreSpec,
    lookup: Dict[int, PyomoObject],
    suffixes: Dict[int, Dict[str, int]],
) -> dict:
    """
    Read a Pyomo component json_str data in from a dict.
    Args:
        obj_dict: dictionary to read from
        store_spec: StoreSpec object specifying what to read in
        lookup: a lookup table for id to component for reading suffixes
        suffixes: a list of suffixes put off reading until end
    Returns:
        Dict
    """

    attr_list = None
    filter_function = None

    pyomo_obj_mapping = {}
    for key, element_dict in obj_dict.items():

        pyomo_class = PYOMO_CLASS_MAPPING[element_dict["__type__"]]

        if attr_list is None:  # assume all items are same
            attr_list, filter_function = store_spec.get_data_class_attr_list(
                pyomo_class
            )

        initialization_dict = {}
        if "expr" in element_dict:
            expr_name, odict = next(iter(element_dict["expr"].items()))
            initialization_dict["expr"] = _read_component(
                {expr_name: odict},
                store_spec,
                lookup=lookup,
                suffixes=suffixes,
                root_name=expr_name,
            )

        elif "args" in element_dict:
            initialization_dict["args"] = [
                _read_component(
                    odict,
                    store_spec,
                    lookup=lookup,
                    suffixes=suffixes,
                    root_name=list(odict.keys())[0],
                )
                for odict in element_dict["args"].values()
            ]

        class_init_params = inspect.signature(pyomo_class.__init__).parameters
        for attr in attr_list:  # read in desired attributes
            if attr in class_init_params:
                if attr == "domain":
                    element_dict[attr] = getattr(pyomo.environ, element_dict[attr])
                initialization_dict[attr] = element_dict[attr]

        pyomo_obj = pyomo_class(**initialization_dict)

        if "__pyomo_components__" in element_dict:
            # read sub-components of block-like
            for component_name, odict in element_dict["__pyomo_components__"].items():
                component = _read_component(
                    {component_name: odict},
                    store_spec,
                    lookup=lookup,
                    suffixes=suffixes,
                    root_name=component_name,
                )
                if isinstance(component_name, Objective) and hasattr(
                    component, "construct"
                ):
                    component._constructed = False
                    component.construct()

                setattr(pyomo_obj, component_name, component)

        if filter_function:
            attr_list = filter_function(pyomo_obj, element_dict)

        pyomo_obj = _set_attributes_from_dict(
            pyomo_obj, element_dict, attr_list, store_spec
        )

        lookup[element_dict["__id__"]] = pyomo_obj
        pyomo_obj_mapping[ast.literal_eval(key)] = pyomo_obj
    return pyomo_obj_mapping


def _set_attributes_from_dict(pyomo_obj, element_dict, attr_list, store_spec) -> object:
    for attr in attr_list:  # read in desired attributes
        if attr not in element_dict:
            if store_spec.ignore_missing:
                continue
            else:
                raise KeyError

        if attr in store_spec.set_functions:
            store_spec.set_functions[attr](pyomo_obj, element_dict[attr])
        else:
            setattr(pyomo_obj, attr, element_dict[attr])
        if isinstance(pyomo_obj, (float, int)) and attr == "value":
            pyomo_obj = element_dict[attr]
    return pyomo_obj


def component_data_from_dict(obj_dict, obj, store_spec: StoreSpec):
    """
    Component data to a dict.
    """
    attr_list, filter_function = store_spec.get_data_class_attr_list(obj)
    if filter_function is not None:
        attr_list = filter_function(obj, obj_dict)

    obj = _set_attributes_from_dict(obj, obj_dict, attr_list, store_spec)

    if may_have_subcomponents(obj):  # read sub-components of block-like
        for _ in obj.component_objects(descend_into=False):
            _read_component(
                obj_dict["__pyomo_components__"], store_spec, dict(), dict()
            )


def _read_suffixes(lookup: Dict[int, PyomoObject], suffixes: Dict[int, Dict[str, int]]):
    """
    Go through the list of suffixes and read the data back in.
    Args:
        lookup: a lookup table to go from id to component
        suffixes: a dictionary with suffix id keys and value dict value
    Returns:
        None
    """
    for uid in suffixes:
        keys = suffixes[uid]
        s = lookup[uid]  # suffixes keys are ids, so get suffix component
        for key in keys:  # set values from value dict
            try:
                kc = lookup[int(key)]  # use int because json turn keys to string
            except KeyError:
                continue
            s[kc] = keys[key]


def from_json(
    obj_dict=None,
    file_name=None,
    json_str=None,
    store_spec: Optional[StoreSpec] = None,
    gz=None,
    root_name=None,
) -> Tuple[Any, Dict[str, float]]:
    """
    Load the state of a Pyomo component state from a dictionary, json file, or
    json string.  Must only specify one of obj_dict, file_name, or s as a non-None value.
    This works by going through the model and loading the state of each
    sub-component of obj. If the saved state contains extra information, it is
    ignored.  If the save state doesn't contain an entry for a model component
    that is to be loaded an error will be raised, unless ignore_missing = True.
    Args:
        obj_dict: State dictionary to load, if None, check file_name and json_str
        file_name: JSON file to load, only used if obj_dict is None
        json_str: JSON string to load only used if both obj_dict and file_name are None
        store_spec: StoreSpec object specifying what to load
        gz: If True assume the file specified by file_name is gzipped. The default is
            True if file_name ends with '.gz' otherwise False.
    Returns:
        Dictionary with some performance information. The keys are
        "load_file_time", how long in seconds it took to load the json file
        "read_dict_time", how long in seconds it took to read models state
        "read_suffixes_time", how long in seconds it took to read suffixes
    """
    start_time = time.time()

    if gz is None:
        if isinstance(file_name, str):
            gz = file_name.endswith(".gz")
        else:
            gz = False

    if obj_dict is not None:  # Existing Python dict (for in-memory stuff).
        pass
    elif file_name is not None:
        if gz:
            with gzip.open(file_name, "r") as f:
                fr = f.read()
                obj_dict = json.loads(fr)
        else:
            with open(file_name, "r") as f:
                obj_dict = json.load(f)
    elif json_str is not None:
        obj_dict = json.loads(json_str)
    else:
        raise Exception("Need to specify a data source to load from")
    load_time = time.time()

    if root_name is None:
        for key in obj_dict:
            if key.startswith("__") and key.endswith("__"):
                continue  # This is metadata or maybe some similar future addition.
            else:
                root_name = key
                break  # should be one root

    if not store_spec:
        store_spec = StoreSpec()

    lookup: Dict[int, PyomoObject] = dict()
    suffixes: Dict[int, Dict[str, int]] = dict()
    obj = _read_component(
        obj_dict, store_spec, lookup=lookup, suffixes=suffixes, root_name=root_name
    )
    read_time = time.time()

    _read_suffixes(lookup, suffixes)
    suffix_time = time.time()

    performance_dict = {
        "load_file_time": load_time - start_time,
        "read_dict_time": read_time - load_time,
        "read_suffixes_time": suffix_time - read_time,
    }
    return obj, performance_dict
