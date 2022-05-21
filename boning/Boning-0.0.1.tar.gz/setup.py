#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2021/3/18 21:43
# @Author : 詹荣瑞
# @File : setup.py
# @desc : 本代码未经授权禁止商用
import boning
from setuptools import setup, find_packages

with open("README.md", "r", encoding='UTF-8') as file:
    long_description = file.read()
extras = {
    'server': ['fastapi', 'pydantic', 'uvicorn>=0.3.0'],
    'parse': ['pyparsing'],
    'command': ['typer'],
}
setup(
    name="Boning",
    version="0.0.1",
    author="六个骨头",
    author_email="2742392377@qq.com",
    description="""
    Boning is a 。
    """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/zrr1999/",
    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(),
    package_data={
        '': ['*.txt'],
        # 包含demo包data文件夹中的 *.dat文件
        'demo': ['data/*.dat'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    platforms="any",
    install_requires=["bonelate", "bonerator"],
    extras_require=extras,
    entry_points={
        # 'console_scripts': [
        #     'bonetex=bonetex:main',
        # ]
    }
)
