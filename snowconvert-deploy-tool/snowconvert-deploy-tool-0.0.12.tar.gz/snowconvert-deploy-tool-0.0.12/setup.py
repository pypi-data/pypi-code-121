#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import os
import platform as _platform
import sys

from setuptools import setup

DEPLOY_VERSION = '0.0.12'

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License'
]

DEPENDENCIES = [
    'snowflake-connector-python>=2.7.7',
    'oscrypto>=1.2.1'
]

setup(
    install_requires=DEPENDENCIES,
    name = 'snowconvert-deploy-tool',
    version=DEPLOY_VERSION,
    description='Mobilize.Net Database Deploy tool for Snowflake',
    license='MIT',
    author='Mobilize.Net',
    author_email='mauricio.rojas@mobilize.net',
    url='https://github.com/MobilizeNet/SnowConvert_Support_Library/tree/main/tools/snowconvert-deploy',
    zip_safe=True,
    long_description=open('README.rst').read(),
    long_description_content_type = "text/x-rst",
    classifiers=CLASSIFIERS,
    scripts=[
        'sc-deploy-db',
        'sc-deploy-db.bat'
    ]
)
