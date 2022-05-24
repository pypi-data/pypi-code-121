#!/usr/bin/python3
# -*- coding: utf-8 -*-

# pkg_find.py file is part of slpkg.

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


from slpkg.messages import Msg
from slpkg.sbo.greps import SBoGrep
from slpkg.pkg.manager import PackageManager
from slpkg.__metadata__ import MetaData as _meta_


class FindFromRepos:
    """Find packages from all enabled repositories
    """
    def __init__(self):
        self.cache = ""
        self.p_cache = ""
        self.find_cache = ""
        self.count_pkg = 0
        self.count_repo = 0
        self.meta = _meta_
        self.msg = Msg()
        self.cyan = self.meta.color["CYAN"]
        self.grey = self.meta.color["GREY"]
        self.endc = self.meta.color["ENDC"]

    def find(self, pkg, flag):
        """Start to find packages and print
        """
        print(f"Packages with name matching [ {self.cyan}"
              f"{', '.join(pkg)}{self.endc} ]\n")
        self.msg.template(78)
        print(f"| Repository Package {' ' * 54}Size")
        self.msg.template(78)
        for repo in _meta_.repositories:
            PACKAGES_TXT = PackageManager(pkg).list_lib(repo)
            packages, sizes = PackageManager(pkg).list_greps(repo,
                                                             PACKAGES_TXT)
            for find, size in zip(packages, sizes):
                for p in pkg:
                    if "--case-ins" in flag:
                        self.p_cache = p.lower()
                        self.find_cache = find.lower()
                    else:
                        self.p_cache = p
                        self.find_cache = find
                    if self.p_cache in self.find_cache:
                        if self.cache != repo:
                            self.count_repo += 1
                        self.cache = repo
                        self.count_pkg += 1
                        ver = self.sbo_version(repo, find)
                        print(f"  {self.cyan}{repo}{self.endc}"
                              f"{' ' * (11 - len(repo))}{find + ver} "
                              f"{' ' * (54 -len(find + ver))}{size:>11}")
        print("\nFound summary")
        print("=" * 79)
        print(f"{self.grey}Total found {self.count_pkg} packages in "
              f"{self.count_repo} repositories.{self.endc}\n")

    def sbo_version(self, repo, find):
        """
        Add version to SBo packages
        """
        ver = ""
        if repo == "sbo":
            ver = f"-{SBoGrep(find).version()}"
        return ver
