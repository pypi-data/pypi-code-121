# -*- coding:utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(name='hgj_spider_download',  # 包名
      version='1.0.3',  # 版本号
      description='hgj-下载器',
      long_description='##版本说明：\n - 1.0.3: 测试版 ,暂且仅支持发送页面请求，不支持sele',
      author='',
      author_email='',
      url='',
      license='',
      install_requires=[
          'requests==2.25.1',
          'redis==3.5.3',
          'gevent==21.1.2'

      ],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Utilities'
      ],
      keywords='',
      packages=find_packages('src'),  # 必填，就是包的代码主目录
      package_dir={'': 'src'},  # 必填
      include_package_data=True,
      )
# !/usr/bin/env python

