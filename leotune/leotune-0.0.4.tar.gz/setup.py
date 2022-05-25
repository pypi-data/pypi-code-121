#!/usr/bin/env Python
# -*- coding: utf-8 -*-
# (Script for Setting-up)
# GNU General Public License v3.0,
#             Copyright (C) 2022 凪坤 (GitHub ID: sandyzikun)
# -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# -*-
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# -*-
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -*-
import setuptools
setuptools.setup(
    name = "leotune",
    version = "0.0.4",
    description = "A Simple Python-based CLI-tool throwing out lyrics of VOCALOID works, which is similar to \"fortune\"",
    long_description = open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/sandyzikun/leotune.git",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        ],
    packages = setuptools.find_packages(),
    package_data = {
        "": ["LICENSE"],
        },
    entry_points = {
        "console_scripts": [
            "leotune=leotune.cli:init",
            ]
        }
    )