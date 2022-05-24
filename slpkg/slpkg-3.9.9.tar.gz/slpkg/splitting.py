#!/usr/bin/python3
# -*- coding: utf-8 -*-

# splitting.py file is part of slpkg.

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


def split_package(package):
    """
    Split package in name, version
    arch and build tag.
    """
    name = ver = arch = build = []
    split = package.split("-")

    if len(split) > 2:
        build = split[-1]
        build_a, build_b = "", ""
        build_a = build[:1]

        if build[1:2].isdigit():
            build_b = build[1:2]

        build = build_a + build_b
        arch = split[-2]
        ver = split[-3]
        name = "-".join(split[:-3])

    return [name, ver, arch, build]
