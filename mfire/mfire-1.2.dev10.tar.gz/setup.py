import os
import setuptools
from datetime import datetime


def get_version(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    fname = os.path.join(here, filename)
    if not os.path.isfile(fname):
        raise RuntimeError(f"Unable to find file : {fname}")
    with open(fname, "r") as fp:
        return fp.readlines()[0].strip()


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mfire",
    version=get_version("mfire/VERSION"),
    license="All rights reserved",
    author="LabIA-MF",
    author_email="lab_ia@meteo.fr",
    description="Code for PROMETHEE project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.meteo.fr/deep_learning/ftap_autom",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
