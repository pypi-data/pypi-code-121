#!/usr/bin/env python3
import os
import pathlib
import shutil

from setuptools import Command
from setuptools import setup

DESC = "Visualize POP hub/sub structures"

VERSION = "9.2.1"

SETUP_DIRNAME = os.path.dirname(__file__)
if not SETUP_DIRNAME:
    SETUP_DIRNAME = os.getcwd()

with open("README.rst", encoding="utf-8") as f:
    LONG_DESC = f.read()

with open(os.path.join("requirements", "base.txt")) as f:
    REQUIREMENTS = f.read().splitlines()

REQUIREMENTS_EXTRA = {"full": set()}
EXTRA_PATH = pathlib.Path("requirements", "extra")
for extra in EXTRA_PATH.iterdir():
    with extra.open("r") as f:
        REQUIREMENTS_EXTRA[extra.stem] = f.read().splitlines()
        REQUIREMENTS_EXTRA["full"].update(REQUIREMENTS_EXTRA[extra.stem])


class Clean(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for subdir in ("pop_create", "pop_docs", "tests"):
            for root, dirs, files in os.walk(
                os.path.join(os.path.dirname(__file__), subdir)
            ):
                for dir_ in dirs:
                    if dir_ == "__pycache__":
                        shutil.rmtree(os.path.join(root, dir_))


def discover_packages():
    modules = []
    for package in ("pop_tree", "pop_doc"):
        for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, package)):
            pdir = os.path.relpath(root, SETUP_DIRNAME)
            modname = pdir.replace(os.sep, ".")
            modules.append(modname)
    return modules


setup(
    name="pop-tree",
    author="Tyler Johnson",
    author_email="tjohnson@saltstack.com",
    url="",
    version=VERSION,
    extras_require=REQUIREMENTS_EXTRA,
    install_requires=REQUIREMENTS,
    description=DESC,
    long_description=LONG_DESC,
    long_description_content_type="text/x-rst",
    python_requires=">=3.6",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 5 - Production/Stable",
    ],
    packages=discover_packages(),
    entry_points={
        "console_scripts": [
            "pop-tree = pop_tree.scripts:start",
            "pop-doc = pop_doc.scripts:start",
        ]
    },
    cmdclass={"clean": Clean},
)
