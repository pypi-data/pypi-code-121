#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sbo_arch.py file is part of slpkg.

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


from slpkg.__metadata__ import MetaData as _meta_


class SBoArch:
    """Manage computer architecture for sbo repository
    """
    def __init__(self):
        self.meta = _meta_
        self.arch = self.meta.arch
        # Architectures
        self.x86 = "i586"
        self.arm = "arm"

    def get(self):
        """Return sbo arch
        """
        if self.arch.startswith("i") and self.arch.endswith("86"):
            self.arch = self.x86
        elif self.meta.arch.startswith("arm"):
            self.arch = self.arm
        return self.arch
