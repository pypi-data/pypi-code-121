# !/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

requirements = ["Pillow", "numpy"]

setup(
    author="Bruno González",
    author_email="brunogllaga@icloud.com",
    name='TIPLSB',
    packages=find_packages(include=['TIPLSB']),
    version='0.0.1',
    description='Library to trace the path of an image based on LSB and RSA.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url='https://github.com/brunogonzalezlla/TIPLSBlib',
    download_url='https://github.com/brunogonzalezlla/TIPLSBlib/archive/v0.1.tar.gz',
    license='MIT',
    classifiers=['Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7'],
)