#!/usr/bin/env python

# Copyright 2014 OpenMarket Ltd
# Copyright 2017 Vector Creations Ltd
# Copyright 2019 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import path
from setuptools import setup

__version__ = '0.1.5-RC1'

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as file:
    readme_file = file.read()

DEPENDENCIES = [
    "awsiotsdk>=1.7.1",
    "requests>=2.26.0",
    "awscrt==0.13.9",
    "awsiotsdk==1.11.0",
    "boto3==1.21.43",
    "botocore==1.24.43",
    "paho-mqtt==1.6.1",
    "urllib3==1.26.8"
]

TEST_DEPENDENCIES = [
    "pretend==1.0.9",
    "pytest==7.1.2",
    "pylint==2.13.9"
]
setup(
    name="signal-application-python-sdk",
    version=__version__,
    packages=['signalsdk'],
    description="signal application services",
    long_description=readme_file,
    long_description_content_type='text/markdown',
    install_requires=DEPENDENCIES,
    test_require=TEST_DEPENDENCIES,
    author='Wesley Clover',
    author_email='burak.cakmak@wesleyclover.com'
)
