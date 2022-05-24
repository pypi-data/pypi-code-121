#!/usr/bin/python3
# -*- coding: utf-8 -*-

# greps.py file is part of slpkg.

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


from functools import lru_cache
from slpkg.utils import Utils
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.slack.slack_version import slack_ver


def repo_data(PACKAGES_TXT, repo, flag):
    """Grap data packages
    """
    (name, location, size, unsize,
     rname, rlocation, rsize, runsize) = ([] for i in range(8))
    for line in PACKAGES_TXT.splitlines():
        if line.startswith("PACKAGE NAME:"):
            name.append(line[15:].strip())
        if line.startswith("PACKAGE LOCATION:"):
            location.append(line[21:].strip())
        if line.startswith("PACKAGE SIZE (compressed):"):
            size.append(line[28:-2].strip())
        if line.startswith("PACKAGE SIZE (uncompressed):"):
            unsize.append(line[30:-2].strip())

    if repo == "slack" and "--upgrade" not in flag:
        (rname,
         rlocation,
         rsize,
         runsize
         ) = slack_filter(name, location, size, unsize, flag)
    elif repo == "rlw":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = rlw_filter(name, location, size, unsize)
    elif repo == "alien":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = alien_filter(name, location, size, unsize)
    elif repo == "rested":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = rested_filter(name, location, size, unsize)
    elif repo == "ktown":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = ktown_filter(name, location, size, unsize)
    else:
        rname, rlocation, rsize, runsize = name, location, size, unsize
    return [rname, rlocation, rsize, runsize]


def slack_filter(name, location, size, unsize, flag):
    """Slackware filter seperate packages from patches/ directory
    """
    (fname, flocation, fsize, funsize) = ([] for i in range(4))

    if "--patches" not in flag:
        for n, l, s, u in zip(name, location, size, unsize):
            if f"_slack{slack_ver()}" not in n:
                fname.append(n)
                flocation.append(l)
                fsize.append(s)
                funsize.append(u)

    if "--patches" in flag:
        for n, l, s, u in zip(name, location, size, unsize):
            if f"_slack{slack_ver()}" in n:
                fname.append(n)
                flocation.append(l)
                fsize.append(s)
                funsize.append(u)

    return [fname, flocation, fsize, funsize]


def rlw_filter(name, location, size, unsize):
    """Filter rlw repository data
    """
    arch = _meta_.arch
    if arch.startswith("i") and arch.endswith("86"):
        arch = "i486"
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        loc = l.split("/")
        if arch == loc[-1]:
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def alien_filter(name, location, size, unsize):
    """Fix to avoid packages include in slackbuilds folder
    """
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        if "slackbuilds" != l:
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def rested_filter(name, location, size, unsize):
    """Filter Alien"s repository data
    """
    ver = slack_ver()
    if _meta_.slack_rel == "current":
        ver = "current"
    path_pkg = "pkg"
    if _meta_.arch == "x86_64":
        path_pkg = "pkg64"
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        if path_pkg == l.split("/")[-2] and ver == l.split("/")[-1]:
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def ktown_filter(name, location, size, unsize):
    """Filter Alien"s ktown repository data
    """
    ver = slack_ver()
    if _meta_.slack_rel == "current":
        ver = "current"
    path_pkg = "x86"
    if _meta_.arch == "x86_64":
        path_pkg = _meta_.arch
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        if (path_pkg in l and _meta_.ktown_kde_repo[1:-1] in l and
                l.startswith(ver)):
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


class Requires:

    def __init__(self, name, repo):
        self.name = name
        self.repo = repo

    def get_deps(self):
        """Grap package requirements from repositories
        """
        if self.repo == "rlw":
            dependencies = {}
            rlw_deps = Utils().read_file(_meta_.conf_path + "rlworkman.deps")
            for line in rlw_deps.splitlines():
                if line and not line.startswith("#"):
                    pkgs = line.split(":")
                    dependencies[pkgs[0]] = pkgs[1]
            if self.name in dependencies.keys():
                return dependencies[self.name].split()
            else:
                return ""
        else:
            PACKAGES_TXT = Utils().read_file(f"{_meta_.lib_path}"
                                             f"{self.repo}_repo/PACKAGES.TXT")
            for line in PACKAGES_TXT.splitlines():
                if line.startswith("PACKAGE NAME:"):
                    pkg_name = split_package(line[14:].strip())[0]
                if line.startswith("PACKAGE REQUIRED:"):
                    if pkg_name == self.name:
                        if line[18:].strip():
                            return self._req_fix(line)

    @lru_cache
    def _req_fix(self, line):
        """Fix slacky and salix requirements because many dependencies
        splitting with "," and others with "|"
        """
        deps = []
        for dep in line[18:].strip().split(","):
            dep = dep.split("|")
            if self.repo == "slacky":
                if len(dep) > 1:
                    for d in dep:
                        deps.append(d.split()[0])
                dep = "".join(dep)
                deps.append(dep.split()[0])
            else:
                if len(dep) > 1:
                    for d in dep:
                        deps.append(d)
                deps.append(dep[0])
        return deps
