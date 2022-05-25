from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

DESCRIPTION = "Python package to do analysis on Occasion"

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, "README.md")) as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="occasion_analysis_package",
    version=1.9,
    author="Anjali Mangla",
    author_email="anjali.m@touchnote.in",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Microsoft :: Windows"]
)
