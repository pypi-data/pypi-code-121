#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r",encoding="utf-8") as f:
  long_description = f.read()

setup(
    name="lcyutils",   # python包的名字
    version="0.0.3",                # 版本号
    description='LCY Personal Tools',           # 描述
    long_description=long_description,                  # 详细描述，这里将readme的内容放置于此
    author='luochengyu',                                      # 作者
    author_email='luochengyu1317@163.com',              # 作者邮箱
    maintainer='luochengyu',                               # 维护人
    maintainer_email='luochengyu1317@163.com',       # 维护人邮箱
    license='MIT License',                                    # 遵守协议
    packages=find_packages(),
    install_requires=[                                               # lamb-common依赖的第三方库
      'requests>=2.26.0',
    ],
    platforms=["all"],                                                # 支持的平台
    url='https://github.com/lcy1317/lcytools',          # github代码仓地址
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',    #对python的最低版本要求
)
