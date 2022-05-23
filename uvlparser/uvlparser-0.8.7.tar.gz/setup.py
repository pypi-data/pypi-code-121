from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="uvlparser",
    version="0.8.7",
    description="This module provides a get_tree function to obtain an ANTLR parse-tree from a UVL-defined feature model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diverso-lab/uvl-diverso",
    author="Pablo Pazo Jiménez",
    author_email="pablopazojim@gmail.com",
    # To find more licenses or classifiers go to: https://pypi.org/classifiers/
    license="GNU General Public License v3 (GPLv3)",
    packages=['uvlparser'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    zip_safe=True,
    python_requires=">=3.0",
    install_requires=[
        "antlr4-python3-runtime==4.7.2",
        "antlr-denter==1.3.1",
    ],
)
