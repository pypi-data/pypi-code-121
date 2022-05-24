#!/usr/bin/python3
# -*- coding: utf-8 -*-

# dependency.py file is part of slpkg.

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


import sys
from functools import lru_cache

from slpkg.__metadata__ import MetaData as _meta_

from slpkg.binary.greps import Requires


class Dependencies:
    """Resolving binary dependencies
    """
    def __init__(self, repo, black):
        self.repo = repo
        self.black = black
        self.dep_results = []
        self.meta = _meta_

    def binary(self, name, flag):
        """Build all dependencies of a package
        """
        if self.meta.rsl_deps in ["on", "ON"] and "--resolve-off" not in flag:
            sys.setrecursionlimit(10000)
            dependencies = []
            requires = Requires(name, self.repo).get_deps()
            if requires:
                for req in requires:
                    if req and req not in self.black:
                        dependencies.append(req)
                self.deep_check(tuple(dependencies), tuple(flag))
            return self.dep_results
        else:
            return []

    @lru_cache
    def deep_check(self, dependencies, flag):
        """Checking if dependencies are finnished
        """
        if dependencies:
            self.dep_results.append(dependencies)
            [self.binary(dep, flag) for dep in dependencies]
