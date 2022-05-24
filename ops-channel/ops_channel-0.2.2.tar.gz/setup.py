#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: jqzhang
# Mail: s_jqzhang@163.com
# Created Time:  2018-11-27 19:17:34
#############################################

from setuptools import setup, find_packages

setup(
    name = "ops_channel",
    version = "0.2.2",
    keywords = ("pip","ops_channel"),
    description = "ops_channel util",
    long_description = "ops_channel util",
    license = "MIT Licence",
    packages=find_packages(),
    url = "https://github.com/sjqzhang/ops_channel",
    author = "jqzhang",
    author_email = "s_jqzhang@163.com",
    include_package_data = True,
    platforms = "any",
)
