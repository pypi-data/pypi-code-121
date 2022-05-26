#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

with open("imetis/README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name = "imetis",
    version = "0.0.2",
    keywords = ["metis", "imetis"],
    description = "A Python SDK for Metis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license = "MIT Licence",

    url = "https://github.com/Jovany-Rong/imetis",
    author = "Jovany-Rong",
    author_email = "amphlie@163.com",

    packages = find_packages(),
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    
    install_requires = ["requests"]
)