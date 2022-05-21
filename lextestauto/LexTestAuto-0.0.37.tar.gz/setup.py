# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : setup.py
# Time       ：2022/2/12 15:51
# Author     ：Lex
# email      : 2983997560@qq.com
# Description：项目描述
"""
from setuptools import setup, find_packages


# 第三方依赖
requires = [
    "pywin32>=303",
    "comtypes>=1.1.0",
    "Pillow>=9.0.1"
]

setup(
    name='LexTestAuto',
    version='0.0.37',
    packages=find_packages(),
    license='MIT',
    author='Lex',
    author_email='2983997560@qq.com',
    description='Lex软件工作室测试包',
    install_requires=requires,  # 第三方库依赖
    zip_safe=False,  # 此项需要，否则卸载时报windows error
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.6',
    package_data={
        '': ['*.dll', "*.pyd"]
    }
)

