# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import inspect
import json
import os
import sys

from sympy2c import Module


def load_core_files(paths, cosmology_config):

    if paths[0].endswith(".ipynb"):
        return extract_code_from_nb(paths, cosmology_config)
    elif paths[0].endswith(".py"):
        return extract_code_from_py(paths, cosmology_config)
    else:
        raise ValueError("can not load from {}".format(paths))


def extract_code_from_nb(path, cosmology_config):

    cells = json.load(open(path))["cells"]
    code = "\n".join(
        "".join(cell["source"])
        for cell in cells
        if (
            cell["cell_type"] == "code"
            and cell["source"]
            and "%%" not in cell["source"][0]
        )
    )

    return _extract_from(code, cosmology_config)


def extract_code_from_py(paths, cosmology_config):

    core_file = import_equations_file(paths, cosmology_config)
    module, checks, enrich_params = setup_wrappers(core_file)
    return module, checks, enrich_params


def import_equations_file(paths, cosmology):

    for path in paths:
        try:
            module_name = os.path.splitext(os.path.basename(path))[0]
            sys.path.insert(0, os.path.dirname(path))
            __builtins__["cosmology"] = cosmology
            sys.modules.pop(module_name, None)
            module = importlib.import_module(module_name)
            module = importlib.reload(module)
            module.__dict__["cosmology"] = cosmology
        finally:
            __builtins__.pop("cosmology", None)
            sys.path.pop(0)
    return module


def setup_wrappers(module):

    from sympy2c import Function, Globals, Ode, OdeCombined, OdeFast, PythonFunction

    m = Module()
    checks = []
    enrich_params = None
    for name, value in module.__dict__.items():
        if isinstance(
            value, (Function, Ode, OdeFast, OdeCombined, Globals, PythonFunction)
        ):
            m.add(value)
        if name.startswith("check"):
            checks.append(value)
        if name == "enrich_params":
            enrich_params = value

    return m, checks, enrich_params


def _extract_from(code, cosmology_config):

    m, ns = Module.parse_sympy_code(code, locals_=dict(cosmology=cosmology_config))

    checks = [
        obj
        for name, obj in ns.items()
        if name.startswith("check") and inspect.isfunction(obj)
    ]

    enrich_params = [obj for name, obj in ns.items() if name == "enrich_params"] + [
        None
    ]

    ns.pop("__builtins__", None)
    return m, checks, enrich_params[0]
