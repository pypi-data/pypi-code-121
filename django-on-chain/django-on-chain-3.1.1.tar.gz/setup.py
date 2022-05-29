#!/usr/bin/env python
from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.in')) as f:
    requirements = f.read().split('\n')

setup(
    name='django-on-chain',
    version='3.1.1',
    description='Django On Chain',
    long_description='The D is silent.',
    license='Closed-Source Proprietary License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=['app', 'tests']),
    include_package_data=True,
    install_requires=requirements,
)
