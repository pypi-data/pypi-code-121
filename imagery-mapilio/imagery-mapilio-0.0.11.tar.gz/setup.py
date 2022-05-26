#!/usr/bin/env python
"""
Mapilio Imagery
"""
from __future__ import (absolute_import, division, print_function)

import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 5):
    raise RuntimeError(
        "Mapilio Calculation supports Python 3.6 and above. "
    )

# This import must be below the above `sys.version_info` check,
# because the code being imported here is not compatible with the older
# versions of Python.
from increment_version import __version__
from imagery.util import __name__

INSTALL_REQUIRES = [
    'calculation-mapilio',
    'solve==0.0.0',
    'trianglesolver==1.2',
    'geopy==2.1.0',
    'opencv-python==4.5.1.48'
]

setup(
    name=__name__,
    version=__version__,
    description='Mapilio Imagery Library',
    url='https://github.com/mapilio/imagery.git',
    author='Mapilio - Ozcan Durak',
    author_email='ozcan@visiosoft.com.tr',
    license='licensed',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.6, <4",
    project_urls={  # Optional
            'Bug Reports': 'https://github.com/mapilio/imagery-tools/issues',
            'Say Thanks!': 'https://mapilio.com/#contact',
            'Source': 'https://github.com/mapilio/imagery-tools/',
        },
)