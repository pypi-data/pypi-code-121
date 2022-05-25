#  Copyright 2022 Data Spree GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import pathlib
from os import path

import pkg_resources
from setuptools import setup

from dataspree.platform_sdk import __version__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name='dataspree-platform-sdk',
    version=__version__,
    author='Data Spree GmbH',
    author_email='info@data-spree.com',
    url='https://data-spree.com/ai',
    license='Apache-2.0',
    description='Python SDK Data Spree AI Platform',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=[
        'dataspree.platform_sdk.decoder'
    ],
    py_modules=[
        'dataspree.platform_sdk.cli',
        'dataspree.platform_sdk.client',
        'dataspree.platform_sdk.query',
        'dataspree.platform_sdk.data_loader',
        'dataspree.platform_sdk.base_model',
        'dataspree.platform_sdk.worker',
        'dataspree.platform_sdk.http_token_authentication'
    ],
    install_requires=install_requires,
    include_package_data=True,
    extras_require={
        'kitti': [],
        'worker': [],
        'build': [
            'pytest~=7.0'
        ]
    },
    entry_points='''
        [console_scripts]
        ds=dataspree.platform_sdk.cli:cli
    ''',
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ]
)
