#!/usr/bin/python3
# -*- coding: utf-8 -*-

# auto_pkg.py file is part of slpkg.

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
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.manager import PackageManager


class AutoInstall:
    """Select Slackware command to install packages
    """
    def __init__(self, packages):
        self.packages = packages
        self.green = _meta_.color["GREEN"]
        self.red = _meta_.color["RED"]
        self.cyan = _meta_.color["CYAN"]
        self.endc = _meta_.color["ENDC"]
        self.msg = Msg()
        self.commands = {
            "i": "installpkg",
            "u": "upgradepkg --install-new",
            "r": "upgradepkg --reinstall"
        }

    def select(self):
        """Select Slackware command
        """
        print("\nDetected Slackware binary package for installation:\n")
        for pkg in self.packages:
            print(" " + pkg.split("/")[-1])
        print()
        self.msg.template(78)
        print("| Choose a Slackware command:")
        self.msg.template(78)
        for com in sorted(self.commands):
            print(f"| {self.red}{com}{self.endc}) {self.green}"
                  f"{self.commands[com]}{self.endc}")
        self.msg.template(78)
        try:
            self.choice = input(" > ")
        except EOFError:
            raise SystemExit("\n")
        if self.choice in self.commands.keys():
            print(f"   \x1b[1A{self.cyan}{self.commands[self.choice]}"
                  f"{self.endc}", end="\n\n")
            print(end="", flush=True)
        self.execute()

    def execute(self):
        """Execute Slackware command
        """
        if self.choice in self.commands.keys():
            if self.choice == "i":
                PackageManager(self.packages).install("")
            elif self.choice in ["u", "r"]:
                PackageManager(self.packages).upgrade(
                    self.commands[self.choice][11:])
