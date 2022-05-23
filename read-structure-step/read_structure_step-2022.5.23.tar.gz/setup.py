#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""read_structure_step
A SEAMM plug-in to read common formats in computational chemistry
"""
import sys
from setuptools import setup, find_packages
import versioneer

short_description = __doc__.splitlines()[1]

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
    name='read_structure_step',
    author="Eliseo Marin-R-Rimoldi",
    author_email='meliseo@vt.edu',
    description=short_description,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license="BSD-3-Clause",
    url='https://github.com/molssi-seamm/read_structure_step',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[] + pytest_runner,
    install_requires=requirements,
    test_suite='tests',
    platforms=['Linux',
               'Mac OS-X',
               'Unix',
               'Windows'],
    zip_safe=True,

    keywords=['SEAMM', 'plug-in', 'flowchart', 'Open Babel', 'molecules',
              'atomistic', 'files'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        "org.molssi.seamm": [
            "Read Structure = read_structure_step:ReadStructureStep",
            "Write Structure = read_structure_step:WriteStructureStep",
        ],
        "org.molssi.seamm.tk": [
            "Read Structure = read_structure_step:ReadStructureStep",
            "Write Structure = read_structure_step:WriteStructureStep",
        ],
    }
)
