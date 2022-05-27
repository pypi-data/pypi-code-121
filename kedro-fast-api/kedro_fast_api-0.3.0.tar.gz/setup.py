#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

requirements = [
    'fastapi',
    'click',
    'uvicorn',
    'pyyaml',
    'kedro>=-0.16'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Artur Wagner",
    author_email='artur.wagner@indicium.tech',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="API to run pickle models with kedro.",
    entry_points={
        'console_scripts': [
            'ika=kedro_fast_api.plugin:commands',
        ],
        "kedro.project_commands": ["kedroapi = kedro_fast_api.plugin:commands"]
    },
    download_url = 'https://bitbucket.org/indiciumtech/kedro_fast_api/get/master.zip',
    install_requires=requirements,
    license="Apache Software License 2.0",
    include_package_data=True,
    keywords='kedro_fast_api',
    name='kedro_fast_api',
    packages=find_packages(include=['kedro_fast_api', 'kedro_fast_api.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://bitbucket.org/indiciumtech/kedro_fast_api',
    version='0.3.0',
    zip_safe=False,
)