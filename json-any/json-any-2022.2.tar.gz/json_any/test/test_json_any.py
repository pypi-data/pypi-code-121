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

from __future__ import annotations

import dataclasses as dtcl
import random as rndm
from array import array as py_array_t
from datetime import date as date_t
from datetime import datetime as date_time_t
from datetime import time as time_t
from datetime import timedelta as time_delta_t
from datetime import timezone as time_zone_t
from enum import Enum as enum_t
from pathlib import Path as path_t
from typing import NamedTuple as named_tuple_base_t
from uuid import UUID as uuid_t

import json_any.json_any as jsny


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


class enum_e(enum_t):
    ONE = 1
    TWO = 2
    THREE = 3


class named_tuple_t(named_tuple_base_t):
    string: str
    integer: int


@dtcl.dataclass
class dataclass_t:
    one: int = 1
    two: int = 2
    three: int = dtcl.field(init=False, default=3)

    @classmethod
    def NewFromJsonDescription(cls, description: dict[str, int]) -> dataclass_t:
        """"""
        three = description["three"]
        del description["three"]

        instance = cls(**description)
        instance.three = three

        return instance


def CheckJsonization(instance: object, /, *, builders=None) -> bool:
    """"""
    jsoned = jsny.JsonStringOf(instance)

    return DecodeAndCompare(jsoned, instance, builders=builders)


def DecodeAndCompare(jsoned: str, instance: object, /, *, builders=None) -> bool:
    """"""
    type_ = type(instance)
    if hasattr(type_, "NewFromJsonString"):
        rebuilt = type_.NewFromJsonString(jsoned)
    else:
        rebuilt = jsny.ObjectFromJsonString(jsoned, builders=builders)

    if type(instance) is type(rebuilt):
        if isinstance(instance, array_t):
            equality = nmpy.array_equal(instance, rebuilt)
        elif isinstance(instance, graph_t):
            equality = grph.utils.misc.graphs_equal(instance, rebuilt)
        else:
            equality = instance == rebuilt
            if not isinstance(equality, bool):
                print(
                    f"{type(instance).__name__}: Cannot check equality of objects of this type"
                )
                return True
        if equality:
            reason = None
        else:
            reason = "Different values"
    else:
        equality = False
        reason = f"Different types ({type(instance)} != {type(rebuilt)})"

    if equality:
        print(type(instance).__name__, "PASSED")
        return True
    else:
        print(instance, "!=", rebuilt, ":", reason)
        return False


if __name__ == "__main__":
    #
    instance_ = py_array_t("b")
    instance_.fromlist([0, 1, 2])
    CheckJsonization(instance_)

    for container_t in (bytes, bytearray, frozenset, set, list, tuple):
        instance_ = container_t([0, 1, 2])
        CheckJsonization(instance_)

    instance_ = named_tuple_t(string="string", integer=123)
    CheckJsonization(
        instance_, builders={type(instance_).__name__: named_tuple_t._make}
    )

    instance_ = date_t(2000, 12, 31)
    CheckJsonization(instance_)
    #
    instance_ = date_time_t(2000, 12, 31, 23, 59, 1)
    CheckJsonization(instance_)
    #
    instance_ = time_t(23, 59, 1)
    CheckJsonization(instance_)
    #
    instance_ = time_delta_t(1, 2, 3)
    CheckJsonization(instance_)
    #
    instance_ = time_zone_t(time_delta_t(seconds=1, microseconds=2), name="fake")
    CheckJsonization(instance_)

    instance_ = enum_e.ONE
    CheckJsonization(instance_, builders={type(instance_).__name__: enum_e})

    instance_ = slice(0, 10, 2)
    CheckJsonization(instance_)

    instance_ = {"one": 1, "two": 2, "three": 3}
    CheckJsonization(instance_)

    instance_ = path_t("/folder/subfolder/file.txt")
    CheckJsonization(instance_)

    instance_ = uuid_t("12345678123456781234567812345678")
    CheckJsonization(instance_)

    instance_ = dataclass_t(10, 20)
    CheckJsonization(
        instance_,
        builders={type(instance_).__name__: dataclass_t.NewFromJsonDescription},
    )

    if nmpy is not None:
        instance_ = nmpy.array([[1, 2, 3], [4, 5, 6]])
        CheckJsonization(instance_)

    if grph is not None:
        instance_ = grph.fast_gnp_random_graph(10, 0.7, seed=0, directed=True)
        grph.set_node_attributes(
            instance_,
            {_nde: rndm.randrange(100) for _nde in instance_.nodes},
            name="attribute",
        )
        grph.set_edge_attributes(
            instance_,
            {_edg: rndm.randrange(100) for _edg in instance_.edges},
            name="attribute",
        )
        CheckJsonization(instance_)

    if pypl is not None:
        instance_, axes = pypl.subplots()
        axes.plot((0, 1, 2), (5, 4, 6), c="g")
        jsoned = jsny.JsonStringOf(instance_)
        rebuilt = jsny.ObjectFromJsonString(jsoned)
        pypl.show()
