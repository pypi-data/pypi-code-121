# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as rt:
    long_description = rt.read()

setup(
    name="lan_download",
    version="0.1.23",
    author="manyougz",
    author_email="25275789@qq.com",
    description=u"提供蓝奏云文件批量下载/获取直链功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://blog.csdn.net/qq_45429426",
    packages=['lan_download'],
    install_requires=[
        "requests>=2.25.0",
        "lxml>=4.6.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)



