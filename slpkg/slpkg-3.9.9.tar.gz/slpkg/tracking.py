#!/usr/bin/python3
# -*- coding: utf-8 -*-

# tracking.py file is part of slpkg.

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
from slpkg.graph import Graph
from slpkg.messages import Msg
from slpkg.blacklist import BlackList
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package

from slpkg.sbo.greps import SBoGrep
from slpkg.sbo.dependency import Requires
from slpkg.sbo.search import sbo_search_pkg

from slpkg.binary.search import search_pkg
from slpkg.binary.dependency import Dependencies


class TrackingDeps(BlackList, Utils):
    """View tree of dependencies and also
    highlight packages with color green
    if already installed and color red
    if not installed.
    """
    def __init__(self, name, repo, flag):
        super().__init__()
        self.name = name
        self.repo = repo
        self.flag = flag
        self.meta = _meta_
        self.msg = Msg()
        self.green = self.meta.color["GREEN"]
        self.yellow = self.meta.color["YELLOW"]
        self.cyan = self.meta.color["CYAN"]
        self.red = self.meta.color["RED"]
        self.endc = self.meta.color["ENDC"]
        self.requires = []
        self.dependencies = []
        self.dependencies_list = []
        self.deps_dict = {}
        self.init_flags()

    def init_flags(self):
        """Flags initialization
        """
        for i in range(0, len(self.flag)):
            if self.flag[i].startswith("--graph="):
                self.image = self.flag[i].split("=")[1]
                self.flag[i] = "--graph="

    def run(self):
        """Run tracking dependencies
        """
        self.msg.resolving()
        self.repositories()
        if self.find_pkg:
            self.dependencies_list.reverse()
            self.requires = self.dimensional_list(self.dependencies_list)
            self.dependencies = self.remove_dbs(self.requires)
            if self.dependencies == []:
                self.dependencies = ["No dependencies"]
            if "--graph=" in self.flag:
                self.deps_tree()
            self.msg.done()
            pkg_len = len(self.name) + 24
            print()    # new line at start
            self.msg.template(pkg_len)
            print(f"| Package {self.cyan}{self.name}{self.endc} "
                  f"dependencies :")
            self.msg.template(pkg_len)
            print("\\")
            print(f" +---{self.yellow}[ Tree of dependencies ]{self.endc}")
            index = 0
            for pkg in self.dependencies:
                if "--check-deps" in self.flag:
                    used = self.check_used(pkg)
                    self.deps_used(pkg, used)
                    used = (f"is dependence on --> "
                            f"{self.cyan}{', '.join(used)}{self.endc}")
                else:
                    used = ""
                index += 1
                installed = ""
                if find_package(f"{pkg}-", self.meta.pkg_path):
                    if self.meta.use_colors in ["off", "OFF"]:
                        installed = "* "
                    print(" |")
                    print(f" +--{index}: {self.green}{pkg}{self.endc} "
                          f"{installed}{used}")
                else:
                    print(" |")
                    print(f" +--{index}: {self.red}{pkg}{self.endc} "
                          f"{installed}")
            if self.meta.use_colors in ["off", "OFF"]:
                print("\n * = Installed\n")
            else:
                print()    # new line at end
            if "--graph=" in self.flag:
                self.graph()
        else:
            self.msg.done()
            raise SystemExit("\nNo package was found to match\n")

    def repositories(self):
        """Get dependencies by repositories
        """
        if self.repo == "sbo":
            self.sbo_case_insensitive()
            self.find_pkg = sbo_search_pkg(self.name)
            if self.find_pkg:
                self.dependencies_list = Requires(self.flag).sbo(self.name)
        else:
            PACKAGES_TXT = self.read_file(
                f"{self.meta.lib_path}{self.repo}_repo/PACKAGES.TXT")
            self.names = list(self.package_name(PACKAGES_TXT))
            self.bin_case_insensitive()
            self.find_pkg = search_pkg(self.name, self.repo)
            if self.find_pkg:
                self.black = list(self.get_black())
                self.dependencies_list = Dependencies(
                    self.repo, self.black).binary(self.name, self.flag)

    def sbo_case_insensitive(self):
        """Matching packages distinguish between uppercase and
        lowercase for sbo repository
        """
        if "--case-ins" in self.flag:
            data = SBoGrep(name="").names()
            data_dict = self.case_sensitive(data)
            for key, value in data_dict.items():
                if key == self.name.lower():
                    self.name = value

    def bin_case_insensitive(self):
        """Matching packages distinguish between uppercase and
        lowercase
        """
        if "--case-ins" in self.flag:
            data_dict = self.case_sensitive(self.names)
            for key, value in data_dict.items():
                if key == self.name.lower():
                    self.name = value

    def graph(self):
        """Drawing image dependencies map
        """
        Graph(self.image).dependencies(self.deps_dict)

    def check_used(self, pkg):
        """Check if dependencies used
        """
        used = []
        dep_path = f"{self.meta.log_path}dep/"
        logs = find_package("", dep_path)
        for log in logs:
            deps = self.read_file(f"{dep_path}{log}")
            for dep in deps.splitlines():
                if pkg == dep:
                    used.append(log)
        return used

    def deps_tree(self):
        """Package dependencies image map file
        """
        dependencies = self.dependencies + [self.name]
        if self.repo == "sbo":
            for dep in dependencies:
                deps = Requires(flag="").sbo(dep)
                if dep not in self.deps_dict.values():
                    self.deps_dict[dep] = self.dimensional_list(deps)
        else:
            for dep in dependencies:
                deps = Dependencies(self.repo, self.black).binary(dep, flag="")
                if dep not in self.deps_dict.values():
                    self.deps_dict[dep] = self.dimensional_list(deps)

    def deps_used(self, pkg, used):
        """Create dependencies dictionary
        """
        if find_package(f"{pkg}-", self.meta.pkg_path):
            if pkg not in self.deps_dict.values():
                self.deps_dict[pkg] = used
            else:
                self.deps_dict[pkg] += used
