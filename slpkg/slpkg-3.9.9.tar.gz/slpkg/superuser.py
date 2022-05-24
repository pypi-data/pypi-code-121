#!/usr/bin/python3
# -*- coding: utf-8 -*-

# superuser.py file is part of slpkg.

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
import getpass


def s_user():
    """Check for root user
    """
    if getpass.getuser() != "root":
        raise SystemExit("\nslpkg: Error: Must have root privileges\n")


def virtual_env():
    """Check if a virtual enviroment exists
    """
    if "VIRTUAL_ENV" in os.environ.keys():
        raise SystemExit("\nslpkg: Error: Please exit from virtual "
                         "environment first\n")
