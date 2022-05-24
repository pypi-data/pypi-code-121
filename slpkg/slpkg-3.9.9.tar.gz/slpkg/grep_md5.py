#!/usr/bin/python3
# -*- coding: utf-8 -*-

# grep_md5.py file is part of slpkg.

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


from slpkg.slack.mirrors import mirrors

from slpkg.url_read import URL
from slpkg.__metadata__ import MetaData as _meta_


def pkg_checksum(binary, repo):
    """Return checksum from CHECKSUMS.md5 file by repository
    """
    md5 = "None"
    if repo == "slack_patches" and _meta_.slack_rel == "stable":
        CHECKSUMS_md5 = URL(mirrors("CHECKSUMS.md5", "patches/")).get_request()
    elif repo == "slack_patches" and _meta_.slack_rel == "current":
        CHECKSUMS_md5 = URL(mirrors("CHECKSUMS.md5", "")).get_request()
    elif repo == "slpkg":
        CHECKSUMS_md5 = URL(_meta_.CHECKSUMS_link).get_request()
    else:
        lib = f"{_meta_.lib_path}{repo}_repo/CHECKSUMS.md5"
        f = open(lib, "r")
        CHECKSUMS_md5 = f.read()
        f.close()
    for line in CHECKSUMS_md5.splitlines():
        if line.endswith(f"/{binary}"):
            md5 = line.split()[0]
    return md5
