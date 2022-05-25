# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hl7v2json",
    version="1.0.0",
    author="John Kharouta",
    author_email="mjolnir117@gmail.com",
    description="A simple library to convert HL7v2 to JSON",
    keywords=[
        'HL7', 'Health Level 7', 'healthcare', 'health care', 'medical record'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kharoutaj/hl7v2json",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={'hl7v2json': ['./data/bamboo/*.json']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'hl7==0.4.5',
        'six==1.11.0'
    ],
    python_requires=">3.6",
)
