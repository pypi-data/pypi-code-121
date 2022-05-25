#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setup.py
# Create source distribution with: python setup.py sdist
#
from distutils.core import setup
from dl2050nn.__config__ import name, package, description, author, author_email, keywords, get_camel
from dl2050nn.__version__ import version

version_camel = get_camel(version)

url = f'https://github.com/jn2050/{name}'
download_url = f'https://github.com/jn2050/{name}/archive/v_{version_camel}.tar.gz'
classifiers=[
      'Development Status :: 4 - Beta', # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Build Tools',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3.7',
]

setup(name=package,
      packages=[package],
      version=version,
      license='MIT',
      description=description,
      author=author,
      author_email=author_email,
      keywords=keywords,
      url=url,
      download_url=download_url,
      classifiers=classifiers
)
