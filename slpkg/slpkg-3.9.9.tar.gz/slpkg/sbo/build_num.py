#!/usr/bin/python3
# -*- coding: utf-8 -*-

# build_num.py file is part of slpkg.

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


import re

from slpkg.utils import Utils
from slpkg.url_read import URL
from slpkg.__metadata__ import MetaData as _meta_


class BuildNumber(Utils):
    """Get build number from SlackBuild script
    """
    def __init__(self, sbo_url, pkg):
        self.sbo_url = sbo_url
        self.pkg = pkg
        self.meta = _meta_

    def get(self):
        num = "NO_BUILD"
        if self.sbo_url:
            SlackBuild = URL(f"{self.sbo_url}"
                             f"{self.pkg}.SlackBuild").get_request()
        else:
            SlackBuild = self.read_file(f"{self.meta.build_path}{self.pkg}/"
                                        f"{self.pkg}.SlackBuild")
        for line in SlackBuild.splitlines():
            line = line.lstrip()
            if line.startswith("BUILD="):
                num = re.findall(r"\d+", line)
                break
        return "".join(num)
