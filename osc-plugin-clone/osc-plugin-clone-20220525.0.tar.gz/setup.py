#!/usr/bin/env python

import os

from setuptools import setup

setup(
    data_files=[
        (os.path.join('lib', 'osc-plugins'), ['clone.py']),
    ],
)
