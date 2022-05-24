#!/usr/bin/python3
# -*- coding: utf-8 -*-

# autobuild.py file is part of slpkg.

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

from slpkg.pkg.build import BuildPackage

from slpkg.sbo.greps import SBoGrep


class AutoBuild:
    """Autobuild package if sources and script is already
    downloaded
    """
    def __init__(self, script, sources, path):
        self.script = script
        self.sources = sources
        self.prgnam = self.script[:-7]
        self.path = path
        self.sbo_sources = []

    def run(self):
        """Build package and fix ordelist per checksum
        """
        self.files_exist()
        self.info_file()
        sources = self.sources
        if len(sources) > 1 and self.sbo_sources != sources:
            sources = self.sbo_sources
        # If the list does not have the same order use from .info
        # order.
        BuildPackage(self.script, sources, self.path, auto=True).build()
        raise SystemExit()

    def info_file(self):
        """Grab sources from .info file and store filename
        """
        sources = SBoGrep(self.prgnam).source().split()
        for source in sources:
            self.sbo_sources.append(source.split("/")[-1])

    def files_exist(self):
        """Check if SlackBuild archive.tar.gz and sources exist
        """
        if not os.path.isfile(self.path + self.script):
            raise SystemExit("\nslpkg: Error: SlackBuild archive.tar.gz "
                             "not found\n")
        for src in self.sources:
            if not os.path.isfile(self.path + src):
                raise SystemExit(f"\nslpkg: Error: Source file '{src}' "
                                 f"not found\n")
