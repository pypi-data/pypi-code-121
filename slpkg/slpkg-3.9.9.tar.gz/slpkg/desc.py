#!/usr/bin/python3
# -*- coding: utf-8 -*-

# desc.py file is part of slpkg.

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
from slpkg.messages import Msg
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.sbo.greps import SBoGrep


class PkgDesc(Utils):
    """Print package description from the repository
    """
    def __init__(self, name, repo, paint):
        self.name = name
        self.repo = repo
        self.paint = paint
        self.meta = _meta_
        self.msg = Msg()
        self.lib = ""
        self.color = {
            "red": self.meta.color["RED"],
            "green": self.meta.color["GREEN"],
            "yellow": self.meta.color["YELLOW"],
            "cyan": self.meta.color["CYAN"],
            "grey": self.meta.color["GREY"],
            "": ""
        }[self.paint]
        if self.repo in self.meta.repositories and self.repo != "sbo":
            self.lib = f"{self.meta.lib_path}{self.repo}_repo/PACKAGES.TXT"

    def view(self):
        """Print package description by repository
        """
        description, count = "", 0
        if self.repo == "sbo":
            description = SBoGrep(self.name).description()
        else:
            PACKAGES_TXT = self.read_file(self.lib)
            for line in PACKAGES_TXT.splitlines():
                if line.startswith(self.name + ":"):
                    description += f"{line[len(self.name) + 2:]}\n"
                    count += 1
                    if count == 11:
                        break
        if description:
            print(f"{self.color}{description}{self.meta.color['ENDC']}")
        else:
            self.msg.pkg_not_found("", self.name, "No matching", "")