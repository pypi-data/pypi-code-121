#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: data@sandquant.com

import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

packages = ['sandinvest']
requires = [
    'pandas',
    'requests',
]

info = {}
with open(os.path.join(here, 'sandinvest', '__version__.py'), 'r', encoding='utf-8') as _version:
    exec(_version.read(), info)

with open("README.md", "r", encoding="utf-8") as _readme:
    readme = _readme.read()

setup(
    name=info['__title__'],
    version=info['__version__'],

    description=info['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',

    author=info['__author__'],
    author_email=info['__author_email__'],

    packages=packages,

    install_requires=requires,
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['SandInvest', 'Data API'],
)
