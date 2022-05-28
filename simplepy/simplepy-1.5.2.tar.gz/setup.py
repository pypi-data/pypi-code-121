#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='simplepy',
    version='1.5.2',
    author='fovegage',
    author_email='fovegage@gmail.com',
    url='https://github.com/fovegage/simplepy',
    description='Python General Toolkit Collection',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
    # install_requires=[
    #     'pysnowflake',
    #     'opencv-python',
    #     'PyCryptodome',
    #     'pandas',
    #     'pymongo',
    #     'redis',
    #     'environs'
    # ],
)
