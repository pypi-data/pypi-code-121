import io
import os
import re

from setuptools import setup, find_packages

import sys

PATH_BASE = os.path.dirname(__file__)


def read_file(fpath):
    """Reads a file within package directories."""
    with io.open(os.path.join(PATH_BASE, fpath)) as f:
        return f.read()


def get_version():
    """Returns version number, without module import (which can lead to ImportError
    if some dependencies are unavailable before install."""
    contents = read_file(os.path.join('vininfo', '__init__.py'))
    version = re.search('VERSION = \\(([^)]+)\\)', contents)
    version = version.group(1).replace(', ', '.').strip()
    return version


with open('README.md', "r") as fh:
    long_description = fh.read()

setup(
    name='wltr-vin',
    version=get_version(),
    url='https://github.com/walteravelino/wltr-vin',

    description='Extracts useful information from Vehicle Identification Number (VIN)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Walter José Avelino da Silva',
    author_email="walter.avelin@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[],
    setup_requires=[] + (['pytest-runner'] if 'test' in sys.argv else []) + [],

    extras_require={
        'cli': ['click'],
    },

    entry_points={
        'console_scripts': ['vininfo = vininfo.cli:main'],
    },

    test_suite='tests',

    tests_require=['pytest'],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
