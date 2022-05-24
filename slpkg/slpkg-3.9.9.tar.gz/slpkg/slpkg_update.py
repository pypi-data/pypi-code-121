#!/usr/bin/python3
# -*- coding: utf-8 -*-

# slpkg_update.py file is part of slpkg.

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
import re
import tarfile
import subprocess

from slpkg.url_read import URL
from slpkg.checksum import check_md5
from slpkg.downloader import Download
from slpkg.grep_md5 import pkg_checksum
from slpkg.__metadata__ import MetaData as _meta_


def it_self_update():
    """Check from GitLab slpkg repository if new version is available
    download and update itself
    """
    __new_version__ = ""
    repository = "gitlab"
    branch = "master"
    ver_link = ("https://{0}.com/{1}/{2}/raw/"
                "{3}/{4}/__metadata__.py".format(repository,
                                                 _meta_.__author__,
                                                 _meta_.__all__,
                                                 branch,
                                                 _meta_.__all__))
    version_data = URL(ver_link).get_request()

    for line in version_data.splitlines():
        line = line.strip()
        if line.startswith("__version_info__"):
            __new_version__ = ".".join(re.findall(r"\d+", line))

    if __new_version__ > _meta_.__version__:
        if _meta_.default_answer in ["y", "Y"]:
            answer = _meta_.default_answer
        else:
            print("\nNew version '{0}-{1}' is available !\n".format(
                _meta_.__all__, __new_version__))
            try:
                answer = input("Would you like to upgrade [y/N]? ")
            except EOFError:
                raise SystemExit("\n")

        if answer in ["y", "Y"]:
            print()   # new line after answer
        else:
            raise SystemExit()

        dwn_link = ["https://{0}.com/{1}/{2}/-/archive/"
                    "{3}/{4}-{5}.tar.gz".format(repository,
                                                _meta_.__author__,
                                                _meta_.__all__,
                                                __new_version__,
                                                _meta_.__all__,
                                                __new_version__)]

        if not os.path.exists(_meta_.build_path):
            os.makedirs(_meta_.build_path)

        Download(_meta_.build_path, dwn_link, repo="").start()
        os.chdir(_meta_.build_path)
        slpkg_tar_file = f"slpkg-{__new_version__}.tar.gz"
        tar = tarfile.open(slpkg_tar_file)
        tar.extractall()
        tar.close()
        file_name = f"{_meta_.__all__}-{__new_version__}"
        os.chdir(file_name)
        check_md5(pkg_checksum(slpkg_tar_file, _meta_.__all__),
                  _meta_.build_path + slpkg_tar_file)
        subprocess.call("chmod +x {0}".format("install.sh"), shell=True)
        subprocess.call("sh install.sh", shell=True)

    else:
        print(f"\n{_meta_.__all__}: There is no new version, "
              "already you use the last!\n")
    raise SystemExit()
