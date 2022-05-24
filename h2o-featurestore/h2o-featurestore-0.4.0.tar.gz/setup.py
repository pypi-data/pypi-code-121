#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='h2o-featurestore',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="0.4.0",
    description='Feature Store Client for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jakubhava/featurestore',
    download_url='https://github.com/jakubhava/featurestore',
    author='H2O.ai',
    author_email='support@h2o.ai',
    license='Apache v2',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8"
    ],
    keywords='machine learning, data mining, statistical analysis, modeling, big data, distributed, parallel',

    # find python packages starting in the current directory
    packages=find_packages(),

    # run-time dependencies
    install_requires=[
        "grpcio>=1.30.0,<=1.43.0",
        "protobuf==3.18.0",
        "jproperties",
        "requests",
        "grpcio-tools>=1.30.0,<=1.43.0"
    ],

    # bundled binary packages
    package_data={
        'featurestore': ['version.txt', '_credentials/roots.pem']},
)
