#!/usr/bin/python
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pg_metadata",
    version="1.1.9",
    author="ish1mura",
    author_email="ek.dummy@gmail.com",
    description="PostgreSQL metadata grabber and comparer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ish1mura/pg_metadata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'psycopg2-binary',
    ],
)
