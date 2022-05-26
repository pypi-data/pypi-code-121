#!/usr/bin/env python3

import os
import runpy

from setuptools import setup, find_packages

def get_version():
    filename = os.path.join(os.path.dirname(__file__), 'savitrigen', '__init__.py')
    var = runpy.run_path(filename)
    return var['__version__']

_VERSION = get_version()

with open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='savitrigen',
    version=_VERSION,
    license='ISC',
    author='João Santos',
    author_email='joaosan177@gmail.com',
    description='Savitri code generator',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    scripts=['scripts/savitrigen'],
    include_package_data=True,
    package_data={
        'savitrigen': [
            'data/config.yml',
            'data/presets/*.yml'
        ]
    },
    install_requires=[
        'multipledispatch==0.6.0',
        'pyyaml==6.0'
    ]
)
