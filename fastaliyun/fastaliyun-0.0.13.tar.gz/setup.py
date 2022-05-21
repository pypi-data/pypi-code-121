#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastaliyun",
    version="0.0.13",
    author="ZeroSeeker",
    author_email="zeroseeker@foxmail.com",
    description="make it easy to use aliyun sdk",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/ZeroSeeker/fastaliyun",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'envx==0.0.5',
        'pydatahub==2.17.2',
        'showlog==0.0.6',
        'urllib3==1.26.8',
        'oss2==2.15.0',
        'fastredis==0.0.22'
    ]
)
