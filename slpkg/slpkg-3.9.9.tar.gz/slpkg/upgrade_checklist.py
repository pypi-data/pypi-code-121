#!/usr/bin/python3
# -*- coding: utf-8 -*-

# upgrade_checklist.py file is part of slpkg.

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


from slpkg.dialog_box import DialogUtil
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.installed import GetFromInstalled


def choose_upg(packages):
    """Creating checklist to choose packages for upgrade
    """
    selected_packages, data = [], []
    if packages:
        for pkg in packages:
            name = GetFromInstalled(pkg).name()
            ver = GetFromInstalled(pkg).version()
            binary = f"{name}-{ver}"
            installed = find_package(binary + _meta_.sp, _meta_.pkg_path)[0]
            data.append(installed)
        text = "Press 'spacebar' to unchoose packages from upgrade"
        title = " Upgrade "
        backtitle = f"{_meta_.__all__} {_meta_.__version__}"
        status = True
        pkgs = DialogUtil(data, text, title, backtitle,
                          status).checklist()
        pkgs = [] if pkgs is None else pkgs
        for pkg in pkgs:
            name = split_package(pkg)[0]
            if name in packages:
                selected_packages.append(name)
        if not selected_packages:
            raise SystemExit(1)
        print()
    return selected_packages
