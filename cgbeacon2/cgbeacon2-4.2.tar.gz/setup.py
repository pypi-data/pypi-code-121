#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from cgbeacon2 import __version__ as version
from setuptools import Command, find_packages, setup

# Package meta-data.
NAME = "cgbeacon2"
DESCRIPTION = "A beacon supporting GA4GH API 1.0"
LONG_DESCRIPTION = "A Python and MongoDB - based beacon supporting GA4GH API v 1.0"
URL = "https://github.com/Clinical-Genomics/cgbeacon2"
EMAIL = "chiara.rasi@scilifelab.se"
AUTHOR = "Chiara Rasi"
KEYWORDS = ["rare diseases", "genomics", "variants", "beacon", "genetic disease"]
LICENSE = "MIT"

here = os.path.abspath(os.path.dirname(__file__))


def parse_reqs(req_path="./requirements.txt"):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with io.open(os.path.join(here, "requirements.txt"), encoding="utf-8") as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle if line.strip() and not line.startswith("#"))

        for line in lines:
            # check for nested requirements files
            if line.startswith("-r"):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])

            else:
                # add the line as a new requirement
                install_requires.append(line)

    return install_requires


REQUIRED = parse_reqs()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, NAME, "__version__.py")) as f:
    exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    download_url="/".join([URL, "tarball", version]),
    keywords=KEYWORDS,
    packages=find_packages(),
    install_requires=REQUIRED,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "Operating System :: MacOS",
        "Operating System :: Unix",
    ],
    entry_points={
        "console_scripts": ["beacon = cgbeacon2.cli.commands:cli"],
    },
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
