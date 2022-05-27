# -*- coding:utf-8 -*-
"""
@Author: Mas0n
@File: setup.py
@Time: 2022/5/27 22:12
@Desc: It's all about getting better.
"""
from setuptools import setup

VERSION = '0.0.2'

with open("README.rst", "rb") as file:
    readme = file.read().decode("utf-8")

setup(
    name='mloguru',  # package name
    version=VERSION,  # package version
    description='self define logger format based on loguru.',  # package description
    long_description=readme,
    packages=["mloguru"],
    zip_safe=False,
    url='https://github.com/Mas0nShi/mloguru',
    author='Mas0n',
    author_email='fishilir@gmail.com',
    install_requires=[
        "loguru>=0.6.0",
    ],
    python_requires=">=3.5",
)
