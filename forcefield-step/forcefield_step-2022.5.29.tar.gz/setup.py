#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""forcefield_step
A SEAMM plug-in for setting up a forcefield or EAM potentials for subsequent simulations.
"""

import sys
from setuptools import setup, find_packages
import versioneer

# from https://github.com/pytest-dev/pytest-runner#conditional-requirement
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as fd:
    requirements = fd.read()

setup(
    # Descriptive entries which should always be present
    name='forcefield_step',
    author="Paul Saxe",
    author_email='psaxe@molssi.org',
    description=__doc__.splitlines()[1],
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='BSD-3-Clause',
    url='https://github.com/molssi-seam/forcefield_step',

    # Which Python importable modules should be included when your package is installed
    # Handled automatically by setuptools. Use 'exclude' to prevent some specific
    # subpackage(s) from being added, if needed
    packages=find_packages(include=['forcefield_step']),

    # Optional include package data to ship with your package
    # Customize MANIFEST.in if the general case does not suit your needs
    # Comment out this line to prevent the files from being packaged with your software
    include_package_data=True,

    # Allows `setup.py test` to work correctly with pytest
    setup_requires=[] + pytest_runner,

    # Required packages, pulls from pip if needed; do not use for Conda
    # deployment
    install_requires=requirements,

    test_suite='tests',
    # tests_require=test_requirements,

    # Valid platforms your code works on, adjust to your flavor
    platforms=['Linux',
               'Mac OS-X',
               'Unix',
               'Windows'],

    # Manual control if final package is compressible or not, set False to
    # prevent the .egg from being made
    # zip_safe=False,

    keywords=['SEAMM', 'plug-in', 'flowchart', 'forcefield', 'EAM', 'OpenKIM'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'org.molssi.seamm': [
            'Forcefield = forcefield_step:ForcefieldStep',
        ],
        'org.molssi.seamm.tk': [
            'Forcefield = forcefield_step:ForcefieldStep',
        ],
    }
)
