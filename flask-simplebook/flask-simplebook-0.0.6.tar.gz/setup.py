#!/usr/bin/env python

from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="flask-simplebook",
    version="0.0.6",
    description="flask app for SimpleBook",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Open Tech Strategies, LLC",
    author_email="frankduncan@opentechstrategies.com",  # For now, this works
    url="https://code.librehq.com/ots/mediawiki/SimpleBook",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    packages=["simplebook"],
    install_requires=[
        "flask",
        "rq",
    ],
    package_dir={"": "."},
    python_requres=">=3.7",
)
