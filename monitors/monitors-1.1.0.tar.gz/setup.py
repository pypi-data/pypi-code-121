#!/usr/bin/env python
# -*- coding:utf-8 -*-
from monitors import __version__
from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="monitors",
    version=__version__,
    keywords=["grafana", "monitors", "process monitor", "system monitor", "influxdb"],
    description="monitor tools",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT Licence",

    url="https://github.com/openutx",
    author="lijiawei",
    author_email="jiawei.li2@qq.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console :: Curses",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Software Development :: Testing",
        "Typing :: Typed",
    ],

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["psutil", "influxdb", "requests", "loguru", "opencv-python>=4.1.2.30,<4.5",
                      "opencv-contrib-python>=4.1.2.30,<4.5",
                      "numpy>=0.18.0",
                      "loguru>=0.2.5",
                      "scikit-image>=0.16.0",
                      "scikit-learn>=0.21.0",
                      "pyecharts>=1.3.1",
                      "findit>=0.5.8",
                      "Jinja2>=2.10.1",
                      "MarkupSafe>=2.0.1",
                      "fire>=0.2.1",
                      "keras>=2.3.1",
                      "pydantic>=0.32.2", ]
)
