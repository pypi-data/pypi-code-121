"""
Setup script for uploading current-path to PyPI.
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


classifiers = """\
Operating System :: OS Independent
Intended Audience :: Developers
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
"""

setuptools.setup(
    name="current-path",
    version="0.0.4",
    author="jon-edward",
    author_email="arithmatlic@gmail.com",
    description="A small library for getting current path data "
                "for a script that imports this library.",
    classifiers=classifiers.splitlines(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jon-edward/current_path",
    package_dir={"current_path": "."},
    py_modules=["current_path"],
    python_requires=">=3.6",
)
