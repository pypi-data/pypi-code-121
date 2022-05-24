#!/usr/bin/python3
# -*- coding: utf-8 -*-

# url_read.py file is part of slpkg.

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


import urllib3

from slpkg.__metadata__ import MetaData as _meta_


class URL:
    """Urls reading class
    """
    def __init__(self, link):
        self.link = link
        self.meta = _meta_
        self.red = _meta_.color["RED"]
        self.endc = _meta_.color["ENDC"]
        if self.meta.http_proxy:
            self.http = urllib3.ProxyManager(self.meta.http_proxy)
        else:
            self.http = urllib3.PoolManager()

    def get_request(self):
        """Open url and read
        """
        try:
            f = self.http.request('GET', self.link)
            return f.data.decode("utf-8", "ignore")
        except urllib3.exceptions.NewConnectionError:
            print(f"\n{self.red}Can't read the file "
                  f"'{self.link.split('/')[-1]}'{self.endc}")
            return " "
