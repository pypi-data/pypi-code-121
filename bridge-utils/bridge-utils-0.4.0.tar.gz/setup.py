#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://packaging.python.org/tutorials/packaging-projects
# docker run -it  -v $PWD:/app  -w /app python:3.8  bash
# python3 -m pip install --user --upgrade twine
# python3 setup.py sdist clean
# python3 setup.py sdist bdist_wheel
# python3 -m twine upload --skip-existing --verbose dist/*

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bridge-utils", # Replace with your own username
    version="0.4.0",
    author="xrgopher",
    author_email='xrgopher@outlook.com',
    url='https://gitlab.com/xrgopher/bridge-utils',
    description="bridge (contract game) utils for PBN & xinrui & bbo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include=['bridge_utils','bridge_utils.*']),
    package_data={'bridge_utils': [
        'pbn2html/*.html',
        'xin2pbn/*.pbn',
        'xin2pbn/template.*',
        'mdbridge/*.md',
        'mdbridge/meta.txt', 
        "xin2pbn/deallog/*"
    ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'mdbridge2html=bridge_utils.mdbridge.mdbridge2html:main',
            'mdbridge2latex=bridge_utils.mdbridge.mdbridge2latex:main',
            'pbn2html=bridge_utils.pbn2html.pbn2html:main',
            'xin2pbn=bridge_utils.xin2pbn.xin2pbn:main',
            'lin2pbn=bridge_utils.lin2pbn.lin2pbn:main',
            'update4suit=bridge_utils.update4suit:main',
            'zyj-update=bridge_utils.update4suit:main',
            'zyj-convert=bridge_utils.zyj2convert:main'
        ],
    },
    install_requires=[
        'requests',
        'markdown'
    ],
    python_requires='>=3.6',
)
