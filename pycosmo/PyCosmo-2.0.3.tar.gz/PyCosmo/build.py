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


import os
import sys

from .Cosmo import Cosmo
from .ini_handling import Bunch
from .config import check_bunch

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_MODEL_INI_FILE = os.path.join(HERE, "model_lcdm.ini")

MODEL_INI_SPEC = {
    "main": {
        "model": str,
        "core_equations_files": list,
        "compilation_flags": [None, str],
        "default_ini_file": "existing_file",
    },
    "equation_parameters": None,
}


def update_nested(original, updates):
    for k, v in updates.items():
        if isinstance(v, dict):
            update_nested(original[k], v)
            continue
        original[k] = v


def build(model_name="lcdm", **extra_settings):
    try:
        return _build(model_name, extra_settings)
    except SystemExit:
        raise
    except Exception as e:
        import pdb
        import traceback

        traceback.print_exc()
        if os.getenv("PDB"):
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            print()
            print("set environment variable PDB to start debugger automatically.")
            raise e


def _build(model_name, extra_settings):

    from .model_config import model_config

    model_config = Bunch(model_config(model_name, extra_settings))

    check_bunch(model_config, MODEL_INI_SPEC)
    return Cosmo(model_config=model_config)
