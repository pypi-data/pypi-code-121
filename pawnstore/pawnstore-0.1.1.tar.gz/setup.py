#!/usr/bin/env python3

# Copyright (c) 2022 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import codecs
import os
import re
from setuptools import setup


PKG_NAME = "pawnstore"
DIRPATH = os.path.dirname(__file__)


def read_rsrc(filename, pypi_compat=False):
    """Return content of filename.
    If pypi_compat is True, remove emojis and anything preceding
    `.. pypi` comment if present.
    """
    with codecs.open(os.path.join(DIRPATH, filename), encoding="utf-8") as _file:
        data = _file.read().strip()
        if pypi_compat or filename == "README.rst":
            if ".. pypi" in data:
                data = re.sub(r":(\w+\\?)+:", "", data[data.find(".. pypi") :] or data)
    return data


with codecs.open("{}/__init__.py".format(PKG_NAME), encoding="utf-8") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

# Deploy: python3 setup.py sdist bdist_wheel; twine upload --verbose dist/*
setup(
    name=PKG_NAME,
    version=version,
    description="chess library to import your PGN games in a local database",
    long_description=read_rsrc("README.rst"),
    author="Fabrice Laporte",
    author_email="kraymer@gmail.com",
    url="https://github.com/KraYmer/pawnstore",
    license="MIT",
    platforms="ALL",
    packages=[
        "pawnstore",
    ],
    install_requires=read_rsrc("requirements.txt").split("\n"),
    python_requires=">=3.6",
    extras_require={
        "test": [
            "coverage>5",
            "pytest>=6",
            "tox>=3",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Environment :: Console",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    keywords="chess",
)
