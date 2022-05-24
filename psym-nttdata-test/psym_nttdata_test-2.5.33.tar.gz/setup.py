#!/usr/bin/env python3

import codecs
import os
import re

import setuptools


def read(*parts):
    with codecs.open(os.path.join(*parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


PSYM_PACKAGES = ["psym", "psym.*"]

this_directory = os.path.abspath(os.path.dirname(__file__))
long_description = ""
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="psym_nttdata_test",
    version=find_version("psym", "common", "constant.py"),
    author="Facebook Inc.",
    url="https://github.com/facebookincubator/symphony",
    description="Tool for accessing and modifying Symphony database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include=PSYM_PACKAGES),
    license="BSD License",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    install_requires=[
        "py-gql-client>=1.0.0",
        "tqdm>=4.32.2",
        "unicodecsv>=0.14.1",
        "requests>=2.22.0",
        "requests-toolbelt>=0.9.1",
        "filetype>=1.0.5",
        "jsonschema",
        "pandas>=0.24.2",
        "xlsxwriter>=1.1.8",
        "dacite>=1.0.2",
    ],
)
