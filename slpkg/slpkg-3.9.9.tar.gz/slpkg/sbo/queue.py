#!/usr/bin/python3
# -*- coding: utf-8 -*-

# queue.py file is part of slpkg.

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
from collections import OrderedDict

from slpkg.utils import Utils
from slpkg.downloader import Download
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager

from slpkg.sbo.greps import SBoGrep
from slpkg.sbo.compressed import SBoLink
from slpkg.sbo.search import sbo_search_pkg
from slpkg.sbo.slack_find import slack_package


class QueuePkgs(Utils):
    """Manage SBo packages, add or remove for building or
    installation
    """
    def __init__(self):
        self.meta = _meta_
        self.green = _meta_.color["GREEN"]
        self.red = _meta_.color["RED"]
        self.endc = _meta_.color["ENDC"]
        self.queue = self.meta.lib_path + "queue/"
        self.queue_list = self.queue + "queue_list"
        self._SOURCES = self.meta.SBo_SOURCES
        self.touch()

    def touch(self):
        """Creating the directories and the queue file
        """
        queue_file = [
            "# In this file you can create a list of\n",
            "# packages you want to build or install.\n",
            "#\n"]
        if not os.path.exists(self.meta.lib_path):
            os.mkdir(self.meta.lib_path)
        if not os.path.exists(self.queue):
            os.mkdir(self.queue)
        if not os.path.isfile(self.queue_list):
            with open(self.queue_list, "w") as queue:
                for line in queue_file:
                    queue.write(line)
        self.queued = self.read_file(self.queue_list)

    def packages(self):
        """Return queue list from /var/lib/queue/queue_list
        file.
        """
        for read in self.queued.splitlines():
            read = read.lstrip()
            if not read.startswith("#"):
                yield read.replace("\n", "")

    def listed(self):
        """Print packages from queue
        """
        print("Packages in the queue:")
        for pkg in self.packages():
            print(f"{self.green}{pkg}{self.endc}")
        print()

    def add(self, pkgs):
        """Add packages in queue if not exist
        """
        queue_list = list(self.packages())
        pkgs = list(OrderedDict.fromkeys(pkgs))
        print("Add packages in the queue:")
        with open(self.queue_list, "a") as queue:
            for pkg in pkgs:
                find = sbo_search_pkg(pkg)
                if pkg not in queue_list and find is not None:
                    print(f"{self.green}{pkg}{self.endc}")
                    queue.write(pkg + "\n")
                else:
                    print(f"{self.red}{pkg}{self.endc}")
        print()

    def remove(self, pkgs):
        """Remove packages from queue
        """
        print("Remove packages from the queue:")
        with open(self.queue_list, "w") as queue:
            for line in self.queued.splitlines():
                if line not in pkgs:
                    queue.write(line + "\n")
                else:
                    print(f"{self.red}{line}{self.endc}")
        print()

    def build(self):
        """Build packages from queue
        """
        sources = []
        packages = list(self.packages())
        if packages:
            for pkg in packages:
                if pkg not in SBoGrep(pkg).names():
                    raise SystemExit(f"\nPackage '{pkg}' was not found in "
                                     f"the SBo repository\n")
                if not os.path.exists(self.meta.build_path):
                    os.mkdir(self.meta.build_path)
                if not os.path.exists(self._SOURCES):
                    os.mkdir(self._SOURCES)
                sbo_url = sbo_search_pkg(pkg)
                sbo_dwn = SBoLink(sbo_url).tar_gz()
                source_dwn = SBoGrep(pkg).source().split()
                os.chdir(self.meta.build_path)
                script = sbo_dwn.split("/")[-1]
                Download(self.meta.build_path, sbo_dwn.split(),
                         repo="sbo").start()
                for src in source_dwn:
                    Download(self._SOURCES, src.split(), repo="sbo").start()
                    sources.append(src.split("/")[-1])
                BuildPackage(script, sources, self.meta.build_path,
                             auto=False).build()
        else:
            raise SystemExit("\nPackages not found in the queue for "
                             "building\n")

    def install(self):
        """Install packages from queue
        """
        packages = list(self.packages())
        if packages:
            print()   # new line at start
            for pkg in packages:
                ver = SBoGrep(pkg).version()
                prgnam = f"{pkg}-{ver}"
                if find_package(prgnam, self.meta.output):
                    binary = slack_package(prgnam)
                    PackageManager(binary).upgrade(flag="--install-new")
                else:
                    print(f"\nPackage {prgnam} not found in the "
                          f"{self.meta.output} for installation\n")
        else:
            raise SystemExit("\nPackages not found in the queue for "
                             "installation\n")
