#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='bluenet-logs',
    version="1.2.0",
    packages=find_packages(exclude=["examples","testing"]),
    author="Crownstone B.V.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crownstone/bluenet-lib-logs",
    install_requires=list(package.strip() for package in open('requirements.txt')),
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ],
    python_requires='>=3.7',
)
