#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: v.stone@163.com


from setuptools import find_packages, setup
import os


URL = 'https://github.com/seoktaehyeon/opsctl'
NAME = 'opsctl'
VERSION = os.getenv('OPSCTL_VER')
DESCRIPTION = 'OPS CTL Tool'
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = DESCRIPTION
AUTHOR = 'Will'
AUTHOR_EMAIL = 'v.stone@163.com'
LICENSE = 'MIT'
PLATFORMS = [
    'any',
]
REQUIRES = [
    'PyYAML',
    'jinja2',
]
CONSOLE_SCRIPTS = 'opsctl=opsctl.main:main'

setup(
    name=NAME,
    version=VERSION,
    description=(
        DESCRIPTION
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    platforms=PLATFORMS,
    url=URL,
    install_requires=REQUIRES,
    entry_points={
        'console_scripts': [CONSOLE_SCRIPTS],
    }
)
