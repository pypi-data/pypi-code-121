#! /usr/bin/env python3
# -*- coding:Utf8 -*-
from setuptools import find_packages, setup

long_description = ""
with open('README.md', encoding='utf-8') as file:
    long_description = file.read()

# -------------------------------------------------------------------------------------------------------------
# Call the setup function:
# -------------------------------------------------------------------------------------------------------------
setup(
    name='nsstools',
    version='0.1.3',
    author='Nicolas Leclerc, Carine Babusiaux, Jean-Louis Halbwachs',
    author_email="gaia.project@obspm.fr",
    licence='CeCILL-2.1',
    description='Tools for calculate campbell and covmat from Gaia CU4 sources',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.obspm.fr/gaia/nsstools.git",
    packages=find_packages(exclude=["tests"]),
    test_suite='tests',
    install_requires=[
        'numpy', 
        'pandas'
    ],
    python_requires='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering :: Astronomy"
    ],
)

