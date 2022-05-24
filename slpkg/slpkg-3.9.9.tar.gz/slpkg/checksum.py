#!/usr/bin/python3
# -*- coding: utf-8 -*-

# checksum.py file is part of slpkg.

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


from slpkg.md5sum import md5
from slpkg.messages import Msg
from slpkg.__metadata__ import MetaData as _meta_


def check_md5(pkg_md5, src_file):
    """MD5 Checksum
    """
    msg = Msg()
    red = _meta_.color["RED"]
    green = _meta_.color["GREEN"]
    endc = _meta_.color["ENDC"]
    if _meta_.checkmd5 in ["on", "ON"]:
        print()
        md5s = md5(src_file)
        if pkg_md5 != md5s:
            msg.template(78)
            print(f"| MD5SUM check for {src_file.split('/')[-1]}"
                  f" [ {red}FAILED{endc} ]")
            msg.template(78)
            print(f"| Expected: {pkg_md5}")
            print(f"| Found: {md5s}")
            msg.template(78)
            print()
            if not msg.answer() in ["y", "Y"]:
                raise SystemExit()
        else:
            msg.template(78)
            print(f"| MD5SUM check for {src_file.split('/')[-1]}"
                  f" [ {green}PASSED{endc} ]")
            msg.template(78)
        print()   # new line after pass checksum
