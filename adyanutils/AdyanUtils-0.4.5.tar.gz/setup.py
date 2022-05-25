#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:42
# @Author  : Adyan
# @File    : setup.py


import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AdyanUtils",
    version="0.4.5",
    author="Adyan",
    author_email="228923910@qq.com",
    description="Special package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/liujiang99/AdyanUtils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests==2.27.1',
        'Faker==13.2.0',
        'Scrapy==2.5.1',
        'scrapy-redis==0.7.2',
        'Twisted==22.1.0',
        'gerapy-pyppeteer==0.2.4',
        'pytz==2021.3',
        'xlrd==2.0.1',
        'xlutils==2.0.0',
        'xlwt==1.3.0',
        'pymongo==3.6.0',
        'pika==1.2.0',
        'redis==4.1.4',
    ],
    python_requires='>=3.7',
)
