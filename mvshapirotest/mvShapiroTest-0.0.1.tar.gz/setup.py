#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 11:00:27 2022

@author: monroy
"""

import setuptools
#from setuptools import setup, find_packages
#from distutils.core import setup
 
with open("README.md", "r") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name = "mvShapiroTest",
    packages = ['mvShapiroTest'],
    version = "0.0.1",
    include_package_data = True, 
    author = "Blanca Monroy-Castillo, Elizabeth González-Estrada",
    author_email = "blancamonroy.96@gmail.com, egonzalez@colpos.mx",
    license = "GPLv3",
    description = "Shapiro-Wilk Test for Multivariate Normality and Skew-Normality",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/CastleMon/goft.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
