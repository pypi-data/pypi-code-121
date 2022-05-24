#!/usr/bin/python3
# -*- coding: utf-8 -*-

# security.py file is part of slpkg.

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


from slpkg.utils import Utils
from slpkg.messages import Msg


def pkg_security(pkgs):
    """Check packages before install or upgrade for security
    reasons. Configuration file in the /etc/slpkg/pkg_security"""
    packages, msg, utils = [], Msg(), Utils()
    security_packages = utils.read_file("/etc/slpkg/pkg_security")
    for read in security_packages.splitlines():
        read = read.lstrip()
        if not read.startswith("#"):
            packages.append(read.replace("\n", ""))
    for p in pkgs:
        for pkg in packages:
            if p == pkg:
                msg.security_pkg(p)
                if not msg.answer() in ["y", "Y"]:
                    raise SystemExit()
