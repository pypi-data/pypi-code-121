#!/usr/bin/python3
# -*- coding: utf-8 -*-

# setup.py file is part of slpkg.

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
import time
from slpkg.__metadata__ import MetaData as _meta_

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

docs_requires = []
tests_requires = []
install_requires = []
optional_requires = [
    "pythondialog>=3.5.1",
    "pygraphviz>=1.3.1"
]

# Non-Python/non-PyPI optional dependencies:
# ascii diagram: graph-easy (available from SBo repository)


def print_logo():
    """print slpkg logo"""
    logo_fname = os.path.join(os.path.dirname(__file__), 'logo.txt')
    with open(logo_fname, 'rb') as f:
        logo = f.read().decode('utf-8')
        print(logo)
        time.sleep(0.5)


print_logo()


setup(
    name="slpkg",
    packages=["slpkg", "slpkg/sbo", "slpkg/pkg", "slpkg/slack",
              "slpkg/binary"],
    scripts=["bin/slpkg"],
    version=_meta_.__version__,
    description="Package manager for Slackware installations",
    long_description=open("README.rst").read(),
    keywords=["slackware", "slpkg", "upgrade", "install", "remove",
              "view", "slackpkg", "tool", "build"],
    author=_meta_.__author__,
    author_email=_meta_.__email__,
    url="https://dslackw.gitlab.io/slpkg/",
    package_data={"": ["LICENSE", "README.rst", "CHANGELOG"]},
    data_files=[("man/man8", ["man/slpkg.8"]),
                ("/etc/bash_completion.d", ["conf/slpkg.bash-completion"]),
                ("/etc/fish/completions", ["conf/slpkg.fish"])],
    install_requires=install_requires,
    extras_require={
        "optional": optional_requires,
        "docs": docs_requires,
        "tests": tests_requires,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Unix Shell",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities"],
    python_requires=">=3.7"
)
