#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from datadis import __version__, __author__

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='datadis-aseme',
    version=__version__,
    description="Herramienta gestión API ASEME DATADIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    provides=['datadis'],
    packages=find_packages(),
    install_requires=requirements,
    license='BSD 3-Clause License',
    author=__author__,
    author_email='devel@gisce.net',
    url = 'https://github.com/gisce/datadis-aseme',
)
