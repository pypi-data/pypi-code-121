#!/usr/bin/python3
# -*- coding: utf-8 -*-

# status_deps.py file is part of slpkg.

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
from slpkg.messages import Msg
from slpkg.graph import Graph
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package


class DependenciesStatus(Utils):
    """Print dependencies status used by packages
    """
    def __init__(self, image):
        self.image = image
        self.meta = _meta_
        self.msg = Msg()
        self.grey = self.meta.color["GREY"]
        self.green = self.meta.color["GREEN"]
        self.endc = self.meta.color["ENDC"]
        self.dmap = {}
        self.count_pkg = 0
        self.count_dep = 0
        self.dep_path = self.meta.log_path + "dep/"
        self.logs = find_package("", self.dep_path)
        if not self.logs:
            self.no_logs()
        self.installed = find_package("", self.meta.pkg_path)

    def data(self):
        """Check all installed packages and create
        dictionary database
        """
        for pkg in self.installed:
            if os.path.isfile(f"{self.meta.pkg_path}{pkg}"):
                name = split_package(pkg)[0]
                for log in self.logs:
                    deps = self.read_file(f"{self.dep_path}{log}")
                    for dep in deps.splitlines():
                        if name == dep:
                            if name not in self.dmap.keys():
                                self.dmap[name] = [log]
                                if not self.count_pkg:
                                    self.count_pkg = 1
                            else:
                                self.dmap[name] += [log]
        self.count_packages()

    def count_packages(self):
        """Count dependencies and packages
        """
        packages = []
        for pkg in self.dmap.values():
            packages += pkg
            self.count_dep += 1
        self.count_pkg = len(set(packages))

    def show(self):
        """Show dependencies status
        """
        self.data()
        print()
        self.msg.template(78)
        print(f"| Dependencies{' ' * 20}Packages")
        self.msg.template(78)
        for key, value in self.dmap.items():
            print("  {0}{1}{2}{3}{4}".format(
                self.green, key, self.endc, " " * (32-len(key)),
                ", ".join(value)))
        self.summary()
        if self.image:
            Graph(self.image).dependencies(self.dmap)

    def tree(self):
        """Like tree view mode
        """
        self.msg.template(78)
        print("| Dependencies\n"
              "| -- Packages")
        self.msg.template(78)
        self.data()
        for pkg, dep in self.dmap.items():
            print(f"+ {self.green}{pkg}{self.endc}")
            print("|")
            for d in dep:
                print(f"+-- {d}")
                print("|")
            print("\x1b[1A \n", end="", flush=True)
        self.summary()
        if self.image:
            Graph(self.image).dependencies(self.dmap)

    def no_logs(self):
        """Print message if no logs found
        """
        raise SystemExit("\n  There were no logs files. "
                         "Obviously not used the\n"
                         "  installation method with the command:\n"
                         "  '$ slpkg -s <repository> <packages>' yet.\n")

    def summary(self):
        """Summary by packages and dependencies
        """
        print("\nStatus summary")
        print("=" * 79)
        print("{0}found {1} dependencies in {2} packages.{3}\n".format(
            self.grey, self.count_dep, self.count_pkg, self.endc))
