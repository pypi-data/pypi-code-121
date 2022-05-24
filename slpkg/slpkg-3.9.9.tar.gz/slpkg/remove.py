#!/usr/bin/python3
# -*- coding: utf-8 -*-

# remove.py file is part of slpkg.

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
import shutil


from slpkg.__metadata__ import MetaData as _meta_


def delete_package(path, packages):
    """Delete downloaded packages
    """
    if _meta_.del_all in ["on", "ON"]:
        for pkg in packages:
            os.remove(f"{path}{pkg}")


def delete_folder(folder):
    """Delete folder with all files.
    """
    if _meta_.del_folder in ["on", "ON"] and os.path.exists(folder):
        shutil.rmtree(folder)
