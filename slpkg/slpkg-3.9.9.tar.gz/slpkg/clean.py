#!/usr/bin/python3
# -*- coding: utf-8 -*-

# clean.py file is part of slpkg.

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


def clean_tmp():
    """Delete packages and sources from tmp/ directory
    """
    tmps = [_meta_.tmp_path,  # /tmp/slpkg/
            _meta_.build_path,  # /tmp/slpkg/build/
            _meta_.slpkg_tmp_packages,  # /tmp/slpkg/packages/
            _meta_.slpkg_tmp_patches  # /tmp/slpkg/patches/
            ]
    # Delete a whole slpkg folder from the tmp directory
    if os.path.exists(tmps[0]):
        shutil.rmtree(tmps[0])
        print(f"All packages and sources were deleted from: {tmps[0]}")
    # Recreate the paths again
    if not os.path.exists(tmps[0]):
        for tmp in tmps:
            print(f"Created directory: {tmp}")
            os.mkdir(tmp)
        print("Done!")