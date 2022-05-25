#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Feini Huang
# Mail: 386899557@qq.com
# Created Time:  2022-4-24 17:09:34
#############################################


from setuptools import setup, find_packages

setup(
    name = "ExplainAI",
    version = "0.2.10",
    keywords = ["pip", "ML","XAI", "visualization"],
    description = "explain AI tool",
    long_description = "file: README.md",
    license = "MIT Licence",

    url = "https://github.com/HuangFeini/ExplainAI",
    author = "Feini Huang",
    author_email = "386899557@qq.com",


    include_package_data = True,
    platforms = "any",
    install_requires = [],


    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    #packages=find_packages(exclude=['ExplainAI']),
    packages=['ExplainAI'],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
        ]},




)


