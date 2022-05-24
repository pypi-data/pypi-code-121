# -*- coding: utf-8 -*-
# COPYRIGHT (C) 2018-2021 GIG.TECH NV
# ALL RIGHTS RESERVED.
#
# ALTHOUGH YOU MAY BE ABLE TO READ THE CONTENT OF THIS FILE, THIS FILE
# CONTAINS CONFIDENTIAL INFORMATION OF GIG.TECH NV. YOU ARE NOT ALLOWED
# TO MODIFY, REPRODUCE, DISCLOSE, PUBLISH OR DISTRIBUTE ITS CONTENT,
# EMBED IT IN OTHER SOFTWARE, OR CREATE DERIVATIVE WORKS, UNLESS PRIOR
# WRITTEN PERMISSION IS OBTAINED FROM GIG.TECH NV.
#
# THE COPYRIGHT NOTICE ABOVE DOES NOT EVIDENCE ANY ACTUAL OR INTENDED
# PUBLICATION OF SUCH SOURCE CODE.
#
# @@license_version:1.9@@


import subprocess
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

NAME = "kmm4g"
VERSION = subprocess.run(
    "cat VERSION || git describe --tags 2>/dev/null || \
    git branch | grep \\* | cut -d ' ' -f2",
    shell=True,
    stdout=subprocess.PIPE,
).stdout.decode("utf8")

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

# with open("requirements.txt") as f:
#    requirements = f.read().splitlines()

setup(
    name=NAME,
    version=VERSION,
    description="Kubernetes MySQL Manager for GIG.tech based clouds.",
    author="Abdalluh Mostafa",
    author_email="abdalluh.mostafa@whitesky.cloud",
    url="https://git.gig.tech/ateam-public/kmm4g",
    keywords=["kmm4g", "kmm", "Kubernetes", "MySQL", "Manager", "GIG"],
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!
    install_requires=[            # I get to this in a second
        'minio>=7.1.4',
        'requests>=2',
    ],
    packages=['kmm4g'],
    package_dir={'kmm4g': 'kmm4g'},
    # Incloud all files for mysql-cluster
    package_data={'kmm4g': ["mysql-cluster/*", "mysql-cluster/*/*"]},
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': ['kmm4g=kmm4g.kmm4g:main']},


)
