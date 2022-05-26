# -*- coding: utf-8 -*-
# @Time: : 2022/5/26 15:17
# @File: setup.py
# @Author : Cooper
# @Software: PyCharm

import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="surlparser",  # 模块名称
    version="1.1",  # 当前版本
    author="Cooper",  # 作者
    author_email="734327367@qq.com",  # 作者邮箱
    description="解析http、https url的一个小工具",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    # url="https://github.com/wupeiqi/fucker",  # 模块github地址
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=[],
    python_requires='>=3.6',
)