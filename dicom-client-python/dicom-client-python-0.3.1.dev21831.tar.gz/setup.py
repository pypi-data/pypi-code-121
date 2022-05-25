# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import setuptools
import os

with open("README_PYPI.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


tag_suffix = ""
if os.environ.get("DEV_VERSION_TAG") != None:
    tag_suffix = ".dev" + os.environ.get("DEV_VERSION_TAG")

setuptools.setup(
    name="dicom-client-python",  # Replace with your own username
    version="0.3.1" + tag_suffix,
    author="Braveheart",
    author_email="bterkaly@microsoft.com",
    description="A small dicom client in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/dicom-client-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pydicom==2.1.1",
        "requests_toolbelt==0.9.1",
        "pyodbc==4.0.30",
        "urllib3==1.26.5",
        "requests==2.25.0",
        "adal==1.2.5",
        "PyJWT==1.7.1",
    ],
)
