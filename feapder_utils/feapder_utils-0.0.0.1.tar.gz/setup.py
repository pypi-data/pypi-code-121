# -*- coding: utf-8 -*-
# @Created : DOLW
# @Time    : 2021/4/17 14:24
# @Project : demo
# @FileName: setup.py
# @Software: PyCharm
# Copyright (c) 2021 DOLW. All rights reserved.


import setuptools
import os
import shutil


def clean_dir(Dir):
    if os.path.isdir(Dir):
        paths = os.listdir(Dir)
        for path in paths:
            filePath = os.path.join(Dir, path)
            if os.path.isfile(filePath):
                os.remove(filePath)
            elif os.path.isdir(filePath):
                if filePath[-4:].lower() == ".svn".lower():
                    continue
                shutil.rmtree(filePath, True)
        os.rmdir(Dir)
    return True


if os.path.exists("dist"):
    clean_dir("dist")

readme = open("README.md", "r", encoding="utf-8")
README_TEXT = readme.read()
readme.close()

setuptools.setup(
    name="feapder_utils",
    version="0.0.0.1",
    author="DOWL",
    author_email="1298528585@qq.com",
    maintainer="DOWL",
    maintainer_email="1298528585@qq.com",
    description="feapder的辅助补充",
    long_description=README_TEXT,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=[".tests", ".tests.", "tests.", "tests"]),
    python_requires=">=3.6",
    platforms="windows10",
    install_requires=[
        "feapder==1.7.5b7",
    ],
)

