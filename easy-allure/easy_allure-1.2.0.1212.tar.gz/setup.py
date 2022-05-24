#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

from easy_allure.main import __version__

setuptools.setup(
    name="easy_allure",
    description="Library for allure testops",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    version=__version__,
    license="Apache-2.0",
    author="2GIS Test Labs",
    url="https://github.com/2gis-test-labs/easy_allure",
    author_email="test-labs@2gis.ru",
    python_requires=">=3.7",
    packages=['easy_allure'],
    entry_points={
        'console_scripts': [
            'easy_allure = easy_allure.main:main',
            'allurectl = easy_allure.main:run_allurectl'
        ]
    },
    package_data={'easy_allure': [
        'bin/*'
    ]},
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
