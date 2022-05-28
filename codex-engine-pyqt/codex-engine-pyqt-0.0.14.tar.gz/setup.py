#! /usr/bin/env python
# -*- coding: utf-8 -*-


import pathlib
from setuptools import setup


here = pathlib.Path(__file__).parent


DESCRIPTION = "A universal translator for serial devices."
LONG_DESCRIPTION = (here / "README.md").read_text()
CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Developers",
    "Development Status :: 4 - Beta",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Widget Sets",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]


setup(
    name="codex-engine-pyqt",
    version="0.0.14",
    packages=["codex", "codex.filters"],
    install_requires=["pyserial", "qtstrap"],
    # setup_requires=[],
    # tests_require=[],
    platforms=["any"],
    author="David Kincaid",
    author_email="dlkincaid0@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=CLASSIFIERS,
    keywords=["codex", "codex engine", "serial"],
    url="https://github.com/Codex-Engine/codex-engine-pyqt"
)