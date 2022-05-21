# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: October 27th 2021 14:42:57 pm
'''

import os
import shutil
import setuptools
from hyssop import Version, __name__

if os.path.isdir('dist'):
    shutil.rmtree('dist')

if os.path.isdir('hyssop.egg-info'):
    shutil.rmtree('hyssop.egg-info')

if os.path.isdir('build'):
    shutil.rmtree('build')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=__name__,
    version=Version,
    author="hsky77",
    author_email="howardlkung@gmail.com",
    description="component-based project hierarchy and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hsky77/hyssop",
    packages=setuptools.find_packages(include=('hyssop', 'hyssop.*')),
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['PyYAML>=5.1.1'],
    python_requires='>=3.6',
    package_data={'': ['*.yml', '*.yaml', '*.csv']}
)
