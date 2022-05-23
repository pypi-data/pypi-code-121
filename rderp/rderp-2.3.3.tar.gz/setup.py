#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    reshapedata LLC
"""
import platform
from setuptools import setup
from setuptools import find_packages

setup(
    name = 'rderp',
    version = '2.3.3',
    install_requires=[
        'requests'
    ],
    packages=find_packages(),
    license = 'Apache License',
    author = 'hulilei',
    author_email = 'hulilei@takewiki.com.cn',
    url = 'http://www.reshapedata.com',
    description = 'erp web api in py language ',
    keywords = ['reshapedata', 'rderp'],
    python_requires='>=3.6',
)
