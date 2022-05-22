#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:lei
@file:setup.py.py
@time:2022/05/22
@邮箱：leigang431@163.com
"""
from setuptools import find_packages, setup

# Package meta-data.
NAME = 'nan5_629'
DESCRIPTION = '南5舍629的兄弟们 by leigang.'
URL = 'https://github.com/leigangblog'
EMAIL = 'leigang431@163.com'
AUTHOR = 'leigang'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.0.1'

# Setting.
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    license="MIT"
)