#!/usr/bin/env python
# -*- coding: utf-8 -*-

# rfc6920, a library to generate and validate RFC6920 URIs
# Copyright (C) 2021 Barcelona Supercomputinh Center, José M. Fernández
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import re
import os
import sys
import setuptools

# In this way, we are sure we are getting
# the installer's version of the library
# not the system's one
setupDir = os.path.dirname(__file__)
sys.path.insert(0, setupDir)

from extended_nc_client import __version__ as pyncclient_ext_version
from extended_nc_client import __author__ as pyncclient_ext_author
from extended_nc_client import __license__ as pyncclient_ext_license

# Populating the long description
readme_path = os.path.join(setupDir, "README.md")
with open(readme_path, "r") as fh:
    long_description = fh.read()

# Populating the install requirements
requirements = []
requirements_path = os.path.join(setupDir, "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path) as f:
        egg = re.compile(r"#[^#]*egg=([^=&]+)")
        for line in f.read().splitlines():
            m = egg.search(line)
            requirements.append(line if m is None else m.group(1))

setuptools.setup(
    name="pyncclient-ext",
    version=pyncclient_ext_version,
    author=pyncclient_ext_author,
    author_email="jose.m.fernandez@bsc.es",
    license=pyncclient_ext_license,
    description="Python extended Nextcloud Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inab/pyncclient-ext",
	project_urls={
		"Bug Tracker": "https://github.com/inab/pyncclient-ext/issues"
	},
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	python_requires=">=3.6",
)
