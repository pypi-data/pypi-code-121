# -*- coding: utf-8 -*-
"""
@Author : Jamie
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(

    name="jamie",
    version="0.1.2",
    author="Jamie",
    author_email="jmzhao29@gmail.com",
    description="A Python package developed for jamie's code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    url="https://github.com/PotatoXi/Jamie",
    project_urls={
        "Bug Tracker": "https://github.com/PotatoXi/Jamie/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    package_dir={'Jamie': 'src'},
    packages=['src'],
    #packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",

)

