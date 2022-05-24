#!/usr/bin/python3
# -*- coding: utf-8 -*-

# check.py file is part of slpkg.

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
from slpkg.blacklist import BlackList
from slpkg.splitting import split_package
from slpkg.upgrade_checklist import choose_upg
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.sbo.greps import SBoGrep


def sbo_upgrade(skip, flag):
    """Return packages for upgrade
    """
    msg = Msg()
    black = BlackList()
    msg.checking()
    upgrade_names = []
    data = SBoGrep(name="").names()
    blacklist = list(black.get_black())
    for pkg in sbo_list():
        name = split_package(pkg)[0]
        ver = split_package(pkg)[1]
        if (name in data and name not in skip and name not in blacklist):
            sbo_package = f"{name}-{SBoGrep(name).version()}"
            package = f"{name}-{ver}"
            if parse_version(sbo_package) > parse_version(package):
                upgrade_names.append(name)
    msg.done()
    if "--checklist" in flag:
        upgrade_names = choose_upg(upgrade_names)
    return upgrade_names


def sbo_list():
    """Return all SBo packages
    """
    for pkg in os.listdir(_meta_.pkg_path):
        if pkg.endswith("_SBo"):
            yield pkg
