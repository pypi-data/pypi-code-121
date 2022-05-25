#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Cython>=0.29.24",
    "numpy",
    "portalocker",
    "requests",
    "sympy<1.4",
]


setup(
    version="1.0.5",  # changing version number here is sufficient!
    author="Uwe Schmitt",
    author_email="uwe.schmitt@id.ethz.ch",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description=("sympy2c is a sympy to c compiler including solving odes at c level."),
    install_requires=requirements,
    license="GPLv3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="sympy2c",
    name="sympy2c",
    packages=find_packages("src"),
    package_dir={"": "src"},
    test_suite="tests",
    zip_safe=False,
)
