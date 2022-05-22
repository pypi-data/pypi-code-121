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

import datetime
import gzip
import json
import time
from typing import Any, Dict, List, Optional

import pyomo.core.base
from pyomo.environ import Suffix

from classiq.interface.pyomo_extension import pyomo

__format_version__ = 1

from classiq.interface.combinatorial_optimization.model_io_comon import (
    StoreSpec,
    may_have_subcomponents,
)


def _can_serialize(obj) -> bool:
    try:
        json.dumps(obj)
        return True
    except TypeError:
        return False


class Counter(object):
    """
    This is a counter object, which is an easy way to pass an integer pointer
    around between methods.
    """

    def __init__(self) -> None:
        self.count = 0


def _may_have_expr(obj) -> bool:
    if hasattr(obj, "expr"):
        return True
    return False


def _may_have_args(obj) -> bool:
    if hasattr(obj, "args"):
        return True
    return False


def _write_component(
    obj_dict: Dict[str, Dict[str, Any]],
    obj,
    store_spec: StoreSpec,
    count,
    lookup,
    suffixes,
):
    """
    Writes a component state to the save dictionary under a key given by the
    components name.
    Args:
        obj_dict: dictionary to to save the object into, will create a key that is the
            object name (not fully qualified)
        obj: object to save
        store_spec: a StoreSpec object indicating what object attributes to write
        count: count the number of Pyomo components written also used for ids
        lookup: is a lookup table for component ids from components
        suffixes: is a list of suffixes, that we are delaying writing
    Returns:
        None
    """

    # Get the component name, doesn't need to be fully qualified or unique because
    # we are storing the state in a hierarchy structure
    if hasattr(obj, "getname"):
        obj_name = obj.getname(fully_qualified=False)
    else:
        obj_name = "noname"

    obj_dict[obj_name] = {"__type__": str(type(obj))}
    if store_spec.include_suffix:
        obj_dict[obj_name]["__id__"] = count.count
    lookup[id(obj)] = count.count
    if count is not None:
        count.count += 1

    attr_list, filter_function = store_spec.get_class_attr_list(obj)
    for attr in attr_list:
        if (
            attr in store_spec.get_functions
            and store_spec.get_functions[attr] is not None
        ):
            obj_dict[obj_name][attr] = store_spec.get_functions[attr](obj)
        else:
            obj_dict[obj_name][attr] = getattr(obj, attr, None)

    obj_dict[obj_name]["data"] = {}

    # if is a suffix, make a list and delay writing data until all components have an assigned id
    if isinstance(obj, Suffix):
        if store_spec.include_suffix:
            if store_spec.suffix_filter is None or obj_name in store_spec.suffix_filter:
                suffixes.append(
                    {
                        "obj_dict": obj_dict[obj_name]["data"],
                        "obj": obj,
                        "store_spec": store_spec,
                        "lookup": lookup,
                    }
                )

    else:
        _write_component_data(
            obj_dict=obj_dict[obj_name]["data"],
            obj=obj,
            store_spec=store_spec,
            count=count,
            lookup=lookup,
            suffixes=suffixes,
        )


def _write_component_data(
    obj_dict,
    obj,
    store_spec,
    count: Counter,
    lookup: Dict[int, int],
    suffixes: List[dict],
) -> None:
    """
    Iterate through the component data and write to the obj_dict dictionary. The keys
    for the data items are added to the dictionary. If the component has
    subcomponents they are written by a recursive call to _write_component under
    the __pyomo_components__ key.
    Args:
        obj_dict: dictionary to to save the object into, will create keys that are the
            data object indexes repn.
        obj: object to save
        store_spec: a StoreSpec object indicating what object attributes to write
        count: count the number of Pyomo components written also used for ids
        lookup: is a lookup table for component ids from components
        suffixes: is a list of suffixes, that we are delaying writing
    Returns:
        None
    """

    if store_spec.include_suffix and isinstance(obj, Suffix):
        for key in obj:
            el = obj[key]
            if id(key) not in lookup:
                # didn't store these components so can't write suffix.
                continue
            if not _can_serialize(el):
                # Since I had the bright idea to expressions in suffixes
                # not everything in a suffix is serializable.
                continue
            obj_dict[lookup[id(key)]] = el  # Assume keys are Pyomo model components
        return

    try:
        item_keys = obj.keys()
    except AttributeError:
        item_keys = [None]

    attr_list: List[str] = []

    for key in item_keys:
        if isinstance(obj, pyomo.core.base.set.Set):
            el = key
        else:
            try:
                el = obj[key]
            except TypeError:
                el = obj

        if not attr_list:  # assume all item are same type, use first to get attr_list
            attr_list, _ = store_spec.get_data_class_attr_list(el)

        repr_dict: Dict[str, Any] = {"__type__": str(type(el))}
        if store_spec.include_suffix:
            repr_dict["__id__"] = count.count
            lookup[id(el)] = count.count

        if count is not None:
            count.count += 1

        for attr in attr_list:  # store desired attributes
            if (
                attr in store_spec.get_functions
                and store_spec.get_functions[attr] is not None
            ):
                repr_dict[attr] = store_spec.get_functions[attr](el)
            else:
                repr_dict[attr] = getattr(el, attr)

        if may_have_subcomponents(el):  # block or block like component
            repr_dict["__pyomo_components__"] = {}
            for component in el.component_objects(descend_into=False):
                _write_component(
                    obj_dict=repr_dict["__pyomo_components__"],
                    obj=component,
                    store_spec=store_spec,
                    count=count,
                    lookup=lookup,
                    suffixes=suffixes,
                )

        if _may_have_expr(el):
            repr_dict["expr"] = {}
            _write_component(
                obj_dict=repr_dict["expr"],
                obj=el.expr,
                store_spec=store_spec,
                count=count,
                lookup=lookup,
                suffixes=suffixes,
            )

        elif _may_have_args(el):
            repr_dict["args"] = {}
            for idx_arg, arg in enumerate(el.args):
                repr_dict["args"][idx_arg] = {}
                _write_component(
                    obj_dict=repr_dict["args"][idx_arg],
                    obj=arg,
                    store_spec=store_spec,
                    count=count,
                    lookup=lookup,
                    suffixes=suffixes,
                )

        obj_dict[repr(key)] = repr_dict


def to_json(
    obj,
    file_name=None,
    human_read=False,
    store_spec=None,
    metadata=None,
    gz=None,
    return_dict=False,
    return_json_string=False,
) -> Optional[Dict[Any, Any]]:
    """
    Save the state of a model to a Python dictionary, and optionally dump it
    to a json file.  To load a model state, a model with the same structure must
    exist.  The model itself cannot be recreated from this.
    Args:
        obj: The Pyomo component object to save.  Usually a Pyomo model, but could
            also be a subcomponent of a model (usually a sub-block).
        file_name: json file name to save model state, if None only create
            python dict
        gz: If file_name is given and gv is True gzip the json file. The default is
            True if the file name ends with '.gz' otherwise False.
        human_read: if True, add indents and spacing to make the json file more
            readable, if false cut out whitespace and make as compact as
            possible
        metadata: A dictionary of additional metadata to add.
        store_spec: is What To Save, this is a StoreSpec object that specifies what
            object types and attributes to save.  If None, the default is used
            which saves the state of the complete model state.
        metadata: additional metadata to save beyond the standard format_version,
            date, and time.
        return_dict: default is False if true returns a dictionary representation
        return_json_string: default is False returns a json string
    Returns:
        If return_dict is True returns a dictionary serialization of the Pyomo
        component.  If return_dict is False and return_json_string is True
        returns a json string dump of the dict.  If file_name is given the dictionary
        is also written to a json file.  If gz is True and file_name is given, writes
        a gzipped json file.
    """
    if gz is None:
        if isinstance(file_name, str):
            gz = file_name.endswith(".gz")
        else:
            gz = False
    if metadata is None:
        metadata = {}

    suffixes: List[dict] = list()
    lookup: Dict[int, int] = dict()
    count: Counter = Counter()
    start_time = time.time()
    if store_spec is None:
        store_spec = StoreSpec()

    now = datetime.datetime.now()
    obj_dict = {
        "__metadata__": {
            "format_version": __format_version__,
            "date": datetime.date.isoformat(now.date()),
            "time": datetime.time.isoformat(now.time()),
            "other": metadata,
        }
    }

    _write_component(obj_dict, obj, store_spec, count, suffixes=suffixes, lookup=lookup)
    for s in suffixes:
        _write_component_data(**s)

    obj_dict["__metadata__"]["__performance__"] = {}
    performance_dict = obj_dict["__metadata__"]["__performance__"]
    performance_dict["n_components"] = count.count
    dict_time = time.time()
    performance_dict["time_to_make_dict"] = dict_time - start_time
    dump_kw: Dict[str, Any] = (
        {"indent": 2} if human_read else {"separators": (",", ":")}
    )
    if file_name is not None:
        if gz:
            with gzip.open(file_name, "w") as f:
                json.dump(obj_dict, f, **dump_kw)
        else:
            with open(file_name, "w") as f:
                json.dump(obj_dict, f, **dump_kw)
    file_time = time.time()
    performance_dict["time_to_write_file"] = file_time - dict_time

    if return_dict:
        return obj_dict
    elif return_json_string:
        return json.dumps(obj_dict, **dump_kw)  # type: ignore[return-value]
    else:
        return None
