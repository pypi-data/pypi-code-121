# This file is part of sympy2c.
#
# Copyright (C) 2013-2022 ETH Zurich, Institute for Particle and Astrophysics and SIS
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
import subprocess
from distutils import ccompiler

from .c_code import LSODA_PATH
from .utils import base_cache_folder, create_folder_if_not_exists, get_platform

CC = ccompiler.new_compiler().executables["compiler"][0]
HERE = os.path.dirname(os.path.abspath(__file__))


def compile_if_needed(target_folder):
    lsoda_out = os.path.join(target_folder, "lsoda.o")
    if not os.path.exists(lsoda_out):
        output = subprocess.check_output(
            [CC, "-c", LSODA_PATH, "-fPIC", "-o", lsoda_out],
            shell=False,
            universal_newlines=True,
        )
        print(output)
    return lsoda_out


def install_lsoda_if_needed(lsoda_root_folder=None):
    if lsoda_root_folder is None:
        lsoda_root_folder = os.path.join(base_cache_folder(), "sympy2c", get_platform())

    target_folder = os.path.join(lsoda_root_folder, "lsoda")
    create_folder_if_not_exists(target_folder)
    object_file = compile_if_needed(target_folder)
    return object_file


if __name__ == "__main__":
    print(install_lsoda_if_needed())
