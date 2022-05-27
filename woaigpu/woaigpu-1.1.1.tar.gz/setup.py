# coding: utf-8
import setuptools
from setuptools import setup

with open('README.md', 'r') as fp:
    readme = fp.read()
 
VERSION = "1.1.1"
LICENSE = "MIT"

setup(
    name='woaigpu',
    version=VERSION,
    description=(
        'I love gpu, using it may lose friends.'
    ),
    long_description=readme,
    author='JunbinGao',
    author_email='junbingao@hust.edu.cn',
    maintainer='JunbinGao',
    maintainer_email='junbingao@hust.edu.cn',
    license=LICENSE,
    packages=setuptools.find_packages(),
    platforms=["all"],
    install_requires=[                 
        'emails',
        'PyEmail',
    ],
    url='https://github.com/gaojunbin/woaigpu',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
)