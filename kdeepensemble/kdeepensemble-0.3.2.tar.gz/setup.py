import os
from glob import glob
from setuptools import setup

exec(open("kdens/version.py").read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kdeepensemble",
    version=__version__,
    description="Deep ensembles for Keras",
    author="Andrew White",
    author_email="andrew.white@rochester.edu",
    url="https://ur-whitelab.github.io/exmol/",
    license="MIT",
    packages=["kdens"],
    install_requires=[
        "numpy",
        "tensorflow",
    ],
    test_suite="tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
