#!/usr/bin/env python
# -*- coding:utf-8 -*-
import codecs
import os
from setuptools import setup, find_packages
pck_name = 'pydumpck'
pck_dict = {}
pck_dict[pck_name] = pck_name
package_dir = os.path.dirname(os.path.realpath(__file__))
long_description = codecs.open(os.path.join(
    package_dir, "README.md"), "r", 'utf-8').read()
about = {}
pck_dir = os.path.join(package_dir, pck_name)
with open(os.path.join(pck_dir, "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

if os.path.exists("requirements.txt"):
    install_requires = open("requirements.txt").read().split("\n")
else:
    install_requires = []

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    package_data={"": ["LICENSE", "NOTICE"]},
    package_dir=pck_dict,
    include_package_data=True,
    python_requires=">=3.7, <4",
    license=about["__license__"],
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=about["__keywords__"],
    long_description=long_description,

    packages=find_packages(),
    platforms='any',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'pydump = main.__main__:main'
        ]
    }
)
