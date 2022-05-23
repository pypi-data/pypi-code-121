# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    README = f.read()


VERSION = '0.4.24'

setup(
    name='otrs_somconnexio',
    version=VERSION,
    author='Coopdevs',
    author_email='info@coopdevs.org',
    url='https://gitlab.com/coopdevs/otrs_somconnexio',
    description='Python package for Somconnexio data syncing in OTRS',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyotrs==0.10.0',
        'future==0.18.2'
    ],
    test_suite='unittest2.collector',
    tests_require=['unittest2', 'mock', 'factory_boy', 'ipdb'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Operating System :: POSIX :: Linux',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
