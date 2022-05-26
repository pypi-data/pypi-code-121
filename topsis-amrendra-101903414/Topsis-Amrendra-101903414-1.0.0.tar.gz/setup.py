import pathlib
from setuptools import setup
import codecs
import os

# Location of file directory
HERE = pathlib.Path(__file__).parent

# Readme
README = (HERE / "README.md").read_text()

VERSION = '1.0.0'
DESCRIPTION = 'Topsis implementation'

# Setting up
setup(
    name="Topsis-Amrendra-101903414",
    version=VERSION,
    author="Amrendra Pratap Singh",
    author_email="singhamrendrapratap19@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url = "",
    license="MIT",
    long_description=README,
    packages=["topsis"],
    install_requires=["pandas", "numpy"],
     classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)