#!/usr/bin/python3
# -*- coding: utf-8 -*-

# load.py file is part of slpkg.

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

from slpkg.utils import Utils
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package


def library(repo):
    """Load packages from slpkg library and from local
    """
    utils = Utils()
    pkg_list, packages = [], ""
    if repo == "sbo":
        if (os.path.isfile(
                f"{_meta_.lib_path}{repo}_repo/SLACKBUILDS.TXT")):
            packages = utils.read_file(
                f"{_meta_.lib_path}{repo}_repo/SLACKBUILDS.TXT")
    else:
        if (os.path.isfile(
                f"{_meta_.lib_path}{repo}_repo/PACKAGES.TXT")):
            packages = utils.read_file(
                f"{_meta_.lib_path}{repo}_repo/PACKAGES.TXT")
    for line in packages.splitlines():
        if repo == "sbo":
            if line.startswith("SLACKBUILD NAME: "):
                pkg_list.append(line[17:].strip())
        elif "local" not in repo:
            if line.startswith("PACKAGE NAME: "):
                pkg_list.append(line[15:].strip())
    if repo == "local":
        pkg_list = find_package("", _meta_.pkg_path)
    return pkg_list


class Regex:
    """Grap packages with simple regex using asterisk *
       with options: starts with string*
                     ends with *string
                     include *string*
    """
    def __init__(self, pkgs):
        self.pkgs = pkgs

    def get(self):
        lib, data = [], []
        for pkg in self.pkgs.split(","):
            pr = pkg.split(":")     # priotity by repository
            data = library(pr[0])   # load data
            if len(pr) > 1:
                for d in data:
                    if pr[1].startswith("*") and pr[1].endswith("*"):
                        if pr[1][1:-1] in d:
                            lib.append(self.add(pr[0], d))
                    elif pr[1].endswith("*"):
                        if d.startswith(pr[1][:-1]):
                            lib.append(self.add(pr[0], d))
                    elif pr[1].startswith("*"):
                        if d.endswith(pr[1][1:]):
                            lib.append(self.add(pr[0], d))
                    else:
                        lib.append(self.add(pr[0], d))
            else:
                lib += pkg.split()
        return lib

    def add(self, repo, pkg):
        """Split packages by repository
        """
        if repo == "sbo":
            return pkg
        else:
            return split_package(pkg)[0]
