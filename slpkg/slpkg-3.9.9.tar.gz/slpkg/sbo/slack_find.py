#!/usr/bin/python3
# -*- coding: utf-8 -*-

# slack_find.py file is part of slpkg.

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
from pkg_resources import parse_version

from slpkg.messages import Msg
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package


def slack_package(prgnam):
    """Return maximum binary Slackware package from output directory
    """
    msg = Msg()
    TAG, binaries, cache, binary = "_SBo", [], "0", ""

    for exp in os.environ.keys():
        if exp == "TAG":
            TAG = os.environ["TAG"]
            break

    for pkg in find_package(prgnam, _meta_.output):
        if pkg.startswith(prgnam) and pkg[:-4].endswith(TAG):
            binaries.append(pkg)

    for bins in binaries:
        binary = bins
        if parse_version(bins) > parse_version(cache):
            binary = bins
            cache = binary

    if not binary:
        msg.pkg_not_found("\n", prgnam, "Can't build", "\n")
        raise SystemExit(1)

    return ["".join(_meta_.output + binary)]
