# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="FlowViewer",
    version="0.0.6",
    author="g1879",
    author_email="g1879@qq.com",
    description="Chrome浏览器数据包监听器。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="FlowViewer",
    url="https://gitee.com/g1879/FlowViewer",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "DrissionPage",
        "requests",
        "pychrome"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.6'
)
