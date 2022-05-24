#!/usr/bin/python3
# -*- coding: utf-8 -*-

# slackware_repo.py file is part of slpkg.

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
from slpkg.binary.greps import repo_data
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_


def slackware_repository():
    """Return all official Slackware packages
    """
    utils = Utils()
    slack_repo, packages, names = [], [], []
    slack_repo = repo_data(
        utils.read_file(f"{_meta_.lib_path}slack_repo/PACKAGES.TXT"),
        "slack", "")
    for pkg in slack_repo[0]:
        names.append(split_package(pkg)[0])
        packages.append(pkg[:-4])
    return packages, names
