# -*- coding: utf-8 -*-
'''
@Time    : 2022/5/17 10:57 AM
@Author  : oujiewen2@shoplineapp.com
@File    : setup.py
'''
import setuptools

requirements = []  # 自定义工具中需要的依赖包

setuptools.setup(
    name="mcHelpers",  # 自定义工具包的名字
    version="6.4",  # 版本号
    author="oujiewen",  # 作者名字
    author_email="oujiewen2@shoplineapp.com",  # 作者邮箱
    description="description",  # 自定义工具包的简介
    license='MIT-0',  # 许可协议
    url="",  # 项目开源地址
    packages=setuptools.find_packages(),  # 自动发现自定义工具包中的所有包和子包
    install_requires=requirements,  # 安装自定义工具包需要依赖的包
    python_requires='>=3.5'  # 自定义工具包对于python版本的要求
)