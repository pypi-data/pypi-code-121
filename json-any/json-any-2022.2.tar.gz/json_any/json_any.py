# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2022)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import dataclasses as dtcl
import json
from array import array as py_array_t
from datetime import date as date_t
from datetime import datetime as date_time_t
from datetime import time as time_t
from datetime import timedelta as time_delta_t
from datetime import timezone as time_zone_t
from enum import Enum as enum_t
from io import BytesIO as bytes_io_t
from pathlib import Path as path_t
from typing import Any, Callable, Dict, GenericAlias, Optional, Tuple, Union
from uuid import UUID as uuid_t

try:
    import matplotlib.pyplot as pypl
except ModuleNotFoundError:
    pypl = None
try:
    import networkx as grph
except ModuleNotFoundError:
    grph = None
try:
    import numpy as nmpy
except ModuleNotFoundError:
    nmpy = None
if nmpy is None:
    blsc = None
    pcst = None
else:
    try:
        import blosc as blsc
    except ModuleNotFoundError:
        blsc = None
    try:
        import pca_b_stream as pcst
    except ModuleNotFoundError:
        pcst = None


builders_h = Dict[str, Callable[[Union[str, dict]], Any]]
description_h = Tuple[str, Any]
# /!\ When a module is not found, using bytes, the first type tested while JSONing, as the main module type is a safe
# way to "disable" it.
if pypl is None:
    figure_t = bytes
else:
    figure_t = pypl.Figure
if grph is None:
    graph_t = bytes
else:
    graph_t = grph.Graph
if nmpy is None:
    array_t = bytes
else:
    array_t = nmpy.ndarray
object_h = Any


_ERROR_MARKER = "!"  # Must be a character forbidden in type names
_TYPES_SEPARATOR = "@"  # Must be a character forbidden in type names


def JsonStringOf(instance: Any, /, *, true_type: Union[Any, type] = None) -> str:
    """"""
    if not ((true_type is None) or (type(true_type) is type)):
        true_type = type(true_type)

    return json.dumps(_JsonDescriptionOf(instance, 0, true_type=true_type))


def _JsonDescriptionOf(
    instance: Any, calling_level: int, /, *, true_type: type = None
) -> description_h:
    """"""
    # Test for high-level classes first since they can also be subclasses of standard classes below, but only if not
    # called from the instance.AsJsonString method, which would create infinite recursion.
    if (calling_level > 0) and hasattr(instance, "AsJsonString"):
        return _JsonDescriptionOf(
            instance.AsJsonString(),
            calling_level + 1,
            true_type=_AutomaticTrueType(instance, true_type),
        )

    if dtcl.is_dataclass(instance):
        # Do not use dtcl.asdict(self) since it recurses into dataclass instances which, if they extend a "container"
        # class like list or dict, will lose the contents.
        as_dict = {
            _fld.name: getattr(instance, _fld.name) for _fld in dtcl.fields(instance)
        }
        true_type = _AutomaticTrueType(instance, true_type)

        return _JsonDescriptionOf(as_dict, calling_level + 1, true_type=true_type)

    error = ""

    if isinstance(instance, GenericAlias):
        instance_type = type(instance).__origin__
    else:
        instance_type = type(instance)

    # /!\ Must be the first type to be tested (see unfoundable modules above)
    if issubclass(instance_type, (bytes, bytearray)):
        # bytes.decode could be used instead of bytes.hex. But which string encoding to use? Apparently, "iso-8859-1" is
        # the appropriate, dummy pass-through codec. To be tested one day...
        base_type, jsonable = type(instance).__name__, instance.hex()
    # Check datetime before date since a datetime is also a date
    elif issubclass(instance_type, date_time_t):
        base_type = "datetime_datetime"
        jsonable = _JsonDescriptionOf(
            (instance.date(), instance.timetz()), calling_level + 1
        )
    elif issubclass(instance_type, date_t):
        base_type = "datetime_date"
        jsonable = (instance.year, instance.month, instance.day)
    elif issubclass(instance_type, time_t):
        base_type = "datetime_time"
        jsonable = (
            instance.hour,
            instance.minute,
            instance.second,
            instance.microsecond,
            _JsonDescriptionOf(instance.tzinfo, calling_level + 1),
            instance.fold,
        )
    elif issubclass(instance_type, time_delta_t):
        base_type = "datetime_timedelta"
        jsonable = (instance.days, instance.seconds, instance.microseconds)
    elif issubclass(instance_type, time_zone_t):
        base_type = "datetime_timezone"
        jsonable = _JsonDescriptionOf(
            (instance.utcoffset(None), instance.tzname(None)), calling_level + 1
        )
    elif issubclass(instance_type, enum_t):
        true_type = _AutomaticTrueType(instance, true_type)
        base_type = "enum_Enum"
        jsonable = _JsonDescriptionOf(instance.value, calling_level + 1)
    elif issubclass(instance_type, py_array_t):
        base_type, jsonable = "array_array", (instance.tolist(), instance.typecode)
    elif issubclass(instance_type, slice):
        base_type, jsonable = "slice", (instance.start, instance.stop, instance.step)
    # Check before looking for tuples since named tuples are subclasses of... tuples
    elif _IsNamedTuple(instance):
        true_type = _AutomaticTrueType(instance, true_type)
        base_type = "typing_NamedTuple"
        jsonable = _JsonDescriptionOf(tuple(instance), calling_level + 1)
    elif issubclass(instance_type, (frozenset, list, set, tuple)):
        base_type = type(instance).__name__
        jsonable = [_JsonDescriptionOf(_elm, calling_level + 1) for _elm in instance]
    elif issubclass(instance_type, dict):
        # json does not accept non-str dictionary keys, hence the json.dumps
        base_type = "dict"
        jsonable = {
            json.dumps(_JsonDescriptionOf(_key, calling_level + 1)): _JsonDescriptionOf(
                _vle, calling_level + 1
            )
            for _key, _vle in instance.items()
        }
    elif issubclass(instance_type, path_t):
        base_type, jsonable = "pathlib_Path", str(instance)
    elif issubclass(instance_type, uuid_t):
        base_type, jsonable = "uuid_UUID", instance.hex
    elif issubclass(instance_type, array_t):
        base_type, jsonable = "numpy_ndarray", _AsMostConcise(instance)
    elif issubclass(instance_type, graph_t):
        edges = grph.to_dict_of_dicts(instance)
        # /!\ Node attributes are added to the edges dictionary! This must be taken into account when deJSONing. Note
        # that several attempts to avoid this have been made, including one relying on repr(node), which is based on
        # hash(node). Since the hash function gives different results across Python sessions, this could not work.
        for node, attributes in instance.nodes(data=True):
            edges[node] = (attributes, edges[node])
        base_type = "networkx_Graph"
        jsonable = (
            _JsonDescriptionOf(edges, calling_level + 1),
            type(instance).__name__,
        )
    elif issubclass(instance_type, figure_t):
        fake_file = bytes_io_t()
        instance.canvas.draw()
        instance.savefig(
            fake_file,
            bbox_inches="tight",
            pad_inches=0.0,
            transparent=True,
            dpi=200.0,
            format="png",
        )
        base_type = "matplotlib_pyplot_Figure"
        jsonable = fake_file.getvalue().hex()
    else:
        base_type = type(instance).__name__
        try:
            _ = json.dumps(instance)
            jsonable = instance
        except TypeError:
            jsonable = None
            error = _ERROR_MARKER
            print(f"{base_type}: UnJSONable type. Using None.")

    if true_type is None:
        true_type = ""
    else:
        true_type = true_type.__name__

    return f"{base_type}{_TYPES_SEPARATOR}{true_type}{error}", jsonable


def ObjectFromJsonString(jsoned: str, /, *, builders: builders_h = None) -> object_h:
    """"""
    return _ObjectFromJsonDescription(json.loads(jsoned), builders=builders)


def _ObjectFromJsonDescription(
    description: description_h,
    /,
    *,
    builders: builders_h = None,
) -> object_h:
    """"""
    types, instance = description
    base_type, true_type = types.split(_TYPES_SEPARATOR)
    if true_type.endswith(_ERROR_MARKER):
        true_type = true_type[: -_ERROR_MARKER.__len__()]
        error = True
    else:
        error = False
    if true_type.__len__() == 0:
        true_type = None
    if builders is None:
        builders = {}

    if error:
        print(
            f"{base_type}{_TYPES_SEPARATOR}{true_type}: UnJSONable type. Returning None."
        )
        return None

    if base_type in ("bytes", "bytearray"):
        if base_type == "bytes":
            output = bytes.fromhex(instance)
        else:
            output = bytearray.fromhex(instance)
    elif base_type == "datetime_datetime":
        date, time = _ObjectFromJsonDescription(instance)
        output = date_time_t(
            date.year,
            date.month,
            date.day,
            time.hour,
            time.minute,
            time.second,
            time.microsecond,
            time.tzinfo,
            fold=time.fold,
        )
    elif base_type == "datetime_date":
        output = date_t(*instance)
    elif base_type == "datetime_time":
        output = time_t(**_TimeDictionaryFromDescription(instance))
    elif base_type == "datetime_timedelta":
        output = time_delta_t(*instance)
    elif base_type == "datetime_timezone":
        time_delta, name = _ObjectFromJsonDescription(instance)
        output = time_zone_t(time_delta, name=name)
    elif base_type == "enum_Enum":
        output = _ObjectFromJsonDescription(instance, builders=builders)
    elif base_type == "array_array":
        as_list, typecode = instance
        output = py_array_t(typecode)
        output.fromlist(as_list)
    elif base_type == "slice":
        output = slice(*instance)
    elif base_type == "typing_NamedTuple":
        output = _ObjectFromJsonDescription(instance, builders=builders)
    elif base_type in ("frozenset", "list", "set", "tuple"):
        iterator = (
            _ObjectFromJsonDescription(_elm, builders=builders) for _elm in instance
        )
        if base_type == "frozenset":
            output = frozenset(iterator)
        elif base_type == "list":
            output = list(iterator)
        elif base_type == "set":
            output = set(iterator)
        else:
            output = tuple(iterator)
    elif base_type == "dict":
        output = {
            _ObjectFromJsonDescription(
                json.loads(_key), builders=builders
            ): _ObjectFromJsonDescription(_vle, builders=builders)
            for _key, _vle in instance.items()
        }
    elif base_type == "pathlib_Path":
        output = path_t(instance)
    elif base_type == "uuid_UUID":
        output = uuid_t(hex=instance)
    elif base_type == "numpy_ndarray":
        output = _AsArray(*instance)
    elif base_type == "networkx_Graph":
        edges_w_attributes, graph_type = instance
        edges_w_attributes = _ObjectFromJsonDescription(
            edges_w_attributes, builders=builders
        )
        graph_type = getattr(grph, graph_type)

        attributes = {}
        edges = {}
        for node, (node_attributes, edge) in edges_w_attributes.items():
            attributes[node] = node_attributes
            edges[node] = edge

        output = grph.from_dict_of_dicts(edges, create_using=graph_type)
        grph.set_node_attributes(output, attributes)
    elif base_type == "matplotlib_pyplot_Figure":
        fake_file = bytes_io_t(bytes.fromhex(instance))
        image = pypl.imread(fake_file)
        output, axes = pypl.subplots()
        axes.set_axis_off()
        axes.matshow(image)
    else:
        output = instance

    if true_type in builders:
        output = builders[true_type](output)
    elif true_type is not None:
        output = None
        print(f"{true_type}: Type without builder. Returning None.")

    return output


def _IsNamedTuple(instance: Any, /) -> bool:
    """"""
    type_ = type(instance)
    if hasattr(type_, "_make"):
        try:
            as_tuple = tuple(instance)
        except TypeError:
            return False

        return type_._make(as_tuple) == instance

    return False


def _AutomaticTrueType(instance: Any, true_type: Optional[type], /) -> type:
    """"""
    if true_type is None:
        return type(instance)

    # This was added to support passing a true type of an object built from a subclass instance. Usage example:
    # decomposition of an instance of a class with multiple inheritance into its components built from the instance
    # itself.
    if issubclass(type(instance), true_type):
        return true_type

    raise ValueError(
        f'{true_type.__name__}: Invalid true type specification for type "{type(instance).__name__}". Expected: None.'
    )


def _TimeDictionaryFromDescription(
    description: Tuple[int, int, int, int, description_h, float], /
) -> Dict[str, Any]:
    """"""
    time_zone = _ObjectFromJsonDescription(description[4])
    return dict(
        zip(
            ("hour", "minute", "second", "microsecond", "tzinfo", "fold"),
            (*description[:4], time_zone, *description[5:]),
        )
    )


def _AsMostConcise(array: array_t, /) -> Tuple[str, str]:
    """"""
    plain = json.dumps((array.tolist(), array.dtype.name))
    versions = [(plain.__len__(), "plain", plain)]

    if blsc is not None:
        packed = blsc.pack_array(array)
        if isinstance(packed, bytes):
            packed = packed.hex()
            how = "blosc.hex"
        else:
            how = "blosc"
        versions.append((packed.__len__(), how, packed))

    if pcst is not None:
        stream = pcst.PCA2BStream(array).hex()
        versions.append((stream.__len__(), "pca_b_stream", stream))

    versions.sort(key=lambda _elm: _elm[0])

    return versions[0][1], versions[0][2]


def _AsArray(how: str, what: str) -> array_t:
    """"""
    if how.startswith("blosc"):
        if how[-1] == "x":
            what = bytes.fromhex(what)
        return blsc.unpack_array(what)

    if how == "pca_b_stream":
        return pcst.BStream2PCA(bytes.fromhex(what))

    data, dtype = json.loads(what)
    return nmpy.array(data, dtype=dtype)
