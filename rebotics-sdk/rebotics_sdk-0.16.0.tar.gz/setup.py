#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

test_requirements = ['pytest', ]

setup(
    author="Malik Sulaimanov",
    author_email='malik@retechlabs.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Rebotics SDK for communicating with Rebotic Services, API CLI client.",
    entry_points={
        'console_scripts': [
            'admin=rebotics_sdk.cli.admin:api',
            'dataset=rebotics_sdk.cli.dataset:api',
            'retailer=rebotics_sdk.cli.retailer:api',
            'rebm=rebotics_sdk.cli.retailer:api',
            'rebotics=rebotics_sdk.cli.common:main',
            'fvm=rebotics_sdk.cli.fvm:api',
            'hawkeye=rebotics_sdk.cli.hawkeye:api',
        ],
    },
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='rebotics_sdk',
    name='rebotics_sdk',
    packages=find_packages(exclude=["tests*"]),
    test_suite='tests',
    url='http://retechlabs.com/rebotics/',
    version='0.16.0',
    zip_safe=False,
    install_requires=[
        'requests>=2.21.0',
        'requests[socks]',
        'requests-toolbelt>=0.9.1',
        'six>=1.12.0',
        'more-itertools',
        'tqdm',
        'chardet',
    ],
    tests_require=test_requirements,
    extras_require={
        'hook': [
            'django',
            'djangorestframework'
        ],
        'shell': [
            'ipython>=7.5.0,<8',
            'pandas',
            'pytz',
            'ptable',
            'python-dateutil',
            'humanize',
            'PySocks>=1.7.1',
            'xlrd>=1.2.0',
            'click>=7.0',
            'pyyaml',
        ]
    }
)
