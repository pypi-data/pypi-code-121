#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys


setup(
    name="aioelschools",
    version="1.0.4",
    author="iamartur",
    description="Async Discord API wrapper for elschool",
    long_description="Async Discord API wrapper for elschool",
    license="MIT",
    url="https://github.com/iamarturr/aioelschools",
    packages=find_packages(),
    install_requires=[
        "pydantic <= 1.9.0",
        "aiohttp <= 3.8.1",
        ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
