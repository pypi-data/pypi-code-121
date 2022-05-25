# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

if os.path.exists('readme.md'):
    long_description = open('readme.md', 'r', encoding='utf8').read()
else:
    long_description = '代码: https://github.com/aitsc/tsc-taskdb'

setup(
    name='tsc-taskdb',
    version='0.4',
    description="taskdb",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='tanshicheng',
    license='GPLv3',
    url='https://github.com/aitsc/tsc-taskdb',
    keywords='tools',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'numpy>=1.18.1',
        'requests>=2.22.0',
        'tinydb==4.5.2',  # https://tinydb.readthedocs.io/en/latest/changelog.html
        'Flask>=1.1.1',
        'pymongo>=3.11',
        'tsc-auto>=0.8.3',
    ],
    python_requires='>=3.6',
)
