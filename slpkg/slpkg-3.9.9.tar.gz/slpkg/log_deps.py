#!/usr/bin/python3
# -*- coding: utf-8 -*-

# log_deps.py file is part of slpkg.

# Copyright 2014-2022 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://gitlab.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os

from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package


def write_deps(deps_dict):
    """Write dependencies in a log file
    into directory `/var/log/slpkg/dep/`
    """
    for name, dependencies in deps_dict.items():
        if find_package(f"{name}-", _meta_.pkg_path):
            dep_path = f"{_meta_.log_path}dep/"
            if not os.path.exists(dep_path):
                os.mkdir(dep_path)
            if os.path.isfile(f"{dep_path}{name}"):
                os.remove(f"{dep_path}{name}")
            if len(dependencies) >= 1:
                with open(f"{dep_path}{name}", "w") as f:
                    for dep in dependencies:
                        f.write(f"{dep}\n")