#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: zengjin
#############################################


from setuptools import setup, find_packages

setup(
    name = "rollbot-crawlab-rollong",
    version = "0.1.16",
    keywords = ("pip", "pathtool","timetool", "magetool", "mage"),
    description = "rollbot crawlab",
    long_description = "rollbot crawlab",
    license = "MIT Licence",

    url = "",
    author = "zengjin",
    author_email = "jzeng@rollong.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)