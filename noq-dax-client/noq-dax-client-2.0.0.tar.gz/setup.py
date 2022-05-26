#!/usr/bin/env python
#
# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#    http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import codecs
import os.path
import re
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

PY2 = sys.version_info[0] == 2

here = os.path.abspath(os.path.dirname(__file__))

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def __init__(self, *args, **kwargs):
        super(PyTest, self).__init__(*args, **kwargs)
        self.pytest_args = None
        self.test_suite = None

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count
            self.pytest_args = ['-n', str(cpu_count()), '--boxed']
        except (ImportError, NotImplementedError):
            self.pytest_args = ['-n', '1', '--boxed']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def read_requirements(filename):
    with open(filename) as requirements:
        return [package.strip() for package in requirements]

packages = [
    'amazondax',
    'amazondax.generated',
    # Both versions must be included since we don't know where it will end up running
    'amazondax.grammar',
    'amazondax.grammar2'
]


install_requires = read_requirements("requirements.txt")
tests_require = read_requirements('requirements-dev.txt')

setup_params = dict(
    name='noq-dax-client',
    version=find_version("amazondax", "__init__.py"),
    author='Amazon Web Services',
    packages=packages,
    url='https://aws.amazon.com/dynamodb/dax/',
    scripts=[],
    license='Apache License 2.0',
    description='Amazon DAX Client for Python',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    python_requires='>=3.6',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ),
)

setup(**setup_params)
