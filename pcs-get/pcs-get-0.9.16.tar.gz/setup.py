# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import pcsget

with open("README.md", "r", encoding='UTF-8') as fp:
    long_desc = fp.read()

setup(
    name="pcs-get",
    version=pcsget.__version__,
    license='GPLv3+',
    author="zhoujianwei.garen",
    author_email="zhoujianwei.garen@bigo.com",
    description="the spider for pcs-protocol",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://git.sysop.bigo.sg/zhoujianwei.garen/pcs-get",
    packages=find_packages(exclude=('tests', 'tests.*')),
    platforms=["all"],
    keywords=["pcs", "bigo", "spider"],
    entry_points={
        'console_scripts': ['pcs-get=pcsget.cmdline:execute']
    },
    classifiers=[
        'Environment :: Console',
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: Chinese (Simplified)",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.8"
    ],
    install_requires=['requests', 'lxml']
)
