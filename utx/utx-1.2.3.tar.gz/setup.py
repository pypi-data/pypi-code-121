#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup, find_packages
from utx import __version__

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="utx",
    version="{}".format(__version__),
    keywords=["utx", "airtest", "pytest", "selenium", "ui", "tools"],
    description='UTX will help you write ui automated tests more easily!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License 2.0',

    url="https://github.com/openutx",
    author="lijiawei",
    author_email="jiawei.li2@qq.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console :: Curses",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    entry_points="""
    [console_scripts]
    utx = utx.cli.cli:main
    """,
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["airtest", "tenacity", "allure-pytest", "pocoui",
                      "tidevice", "faker", "jmespath", "loguru", "pytest-xdist",
                      "PyYAML", "allure-python-commons", "pytest-rerunfailures", "pyOpenSSL",
                      "pyasn1", "selenium~=3.14.0", "pynput", "tqdm", "popups", "webdriver-manager"]

)
