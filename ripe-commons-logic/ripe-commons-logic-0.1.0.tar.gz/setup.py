#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

setuptools.setup(
    name="ripe-commons-logic",
    version="0.1.0",
    author="Platforme International",
    author_email="development@platforme.com",
    description="RIPE Commons Logic",
    license="Apache License, Version 2.0",
    keywords="ripe commons business logic",
    url="http://www.platforme.com",
    zip_safe=False,
    packages=["ripe_commons_logic"],
    test_suite = "ripe_commons_logic.test",
    package_dir={"": os.path.normpath("src")},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    long_description=open(
        os.path.join(os.path.dirname(__file__), "README.md"), "r"
    ).read(),
    long_description_content_type="text/markdown",
)
