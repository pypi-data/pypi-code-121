#!/usr/bin/python3
# -*- coding: utf-8 -*-

# mirrors.py file is part of slpkg.

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


from slpkg.repositories import Repo
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.slack.slack_version import slack_ver


def mirrors(name, location):
    """Select Slackware official mirror packages
       based architecture and version.
    """
    rel = _meta_.slack_rel
    ver = slack_ver()
    repo = Repo()
    slack = repo.slack()
    if _meta_.arch == "x86_64":
        if rel == "stable":
            http = f"{slack}slackware64-{ver}/{location}{name}"
        else:
            http = f"{slack}slackware64-{rel}/{location}{name}"
    elif _meta_.arch.startswith("arm"):
        if rel == "stable":
            http = f"{slack}slackwarearm-{ver}/{location}{name}"
        else:
            http = f"{slack}slackwarearm-{rel}/{location}{name}"
    else:
        if rel == "stable":
            http = f"{slack}slackware-{ver}/{location}{name}"
        else:
            http = f"{slack}slackware-{rel}/{location}{name}"
    return http
