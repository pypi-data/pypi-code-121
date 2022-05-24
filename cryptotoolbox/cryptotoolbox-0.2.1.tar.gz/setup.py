#!/usr/bin/env python3
# coding: utf-8

""" Setup script. """

# Built-in packages
from setuptools import setup, find_packages


# Set this to True to enable building extensions using Cython.
# Set it to False to build extensions from the C file (that
# was previously created using Cython).
USE_CYTHON = 'auto'

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Financial and Insurance Industry',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.8',
    'Topic :: Office/Business :: Financial',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
]

MAJOR = 1
MINOR = 0
PATCH = 8
VERSION = '{}.{}.{}'.format(MAJOR, MINOR, PATCH)

DESCRIPTION = 'Python scripts of machine learning, econometrics, statistical tools'

build_requires = [
    'matplotlib>=3.0.1',
    'numpy>=1.15.3',
    'pandas>=1.0.1',
    'pickle5',
    'scipy>=1.2.0',
    'seaborn>=0.9.0',
    'boto3',
    'python-binance',
    'pykalman',
    'pyhht',
    'PyWavelets',
#    'numba==0.50.1',
    'numba',
    'pmdarima',
    'ccxt',
    'dash==1.13.3',
    'dropbox',
    'dash-bootstrap-components',
    'bitmex',
    'python-binance',
    'llvmlite'
#    'llvmlite==0.33.0'
]
build_requires=[]

setup(
    name='cryptotoolbox',
    version='0.2.1',
    packages=find_packages(),
    download_url='https://github.com/sduprey/cryptotoolbox/archive/0.0.tar.gz',
    author='stefan duprey',
    author_email='stefan.duprey@gmail.com',
    description='Dashboard for financial market data',
    license='MIT',
    install_requires=build_requires,
    classifiers=CLASSIFIERS,
)
# python setup.py sdist
#twine upload dist/* (stef564 dashlane)
#pip install cryptotoolbox==0.0?
