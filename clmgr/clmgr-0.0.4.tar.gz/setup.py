import io
import os
import versioneer
from setuptools import setup

# Package meta-data
NAME = "clmgr"
DESCRIPTION = "Copyright License Manager"
URL = "https://github.com/enovationgroup/copyright-license-manager"
AUTHOR = "Enovation Group"
EMAIL = "development@enovationgroup.com"
REQUIRES_PYTHON = ">3.8"
LICENSE = "MIT"

cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, "README.rst"), encoding="utf-8", mode="r") as fh:
    long_description = "\n" + fh.read()

with io.open(os.path.join(cwd, "requirements.txt"), encoding="utf-8", mode="r") as fh:
    requirements = [line.strip() for line in fh]

setup(
    name=NAME,
    version=versioneer.get_version(),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    py_modules=["clmgr"],
    entry_points={
        "console_scripts": ["clmgr=clmgr.main:main"],
    },
    install_requires=requirements,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    # $ setup.py publish support.
    cmdclass={"versioneer": versioneer.get_cmdclass()},
)
