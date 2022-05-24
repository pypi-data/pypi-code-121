# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from multiprocessing import cpu_count

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


def get_version() -> str:
  # https://packaging.python.org/guides/single-sourcing-package-version/
  with open(os.path.join("mjc_mwe", "__init__.py"), "r") as f:
    init = f.read().split()
  return init[init.index("__version__") + 2][1:-1]


def get_description():
  with open("README.md", encoding="utf8") as f:
    return f.read()


setup(
  name="mjc_mwe",
  version=get_version(),
  author="Jiayi Weng",
  author_email="trinkle23897@gmail.com",
  url="https://github.com/Trinkle23897/mjc-mwe",
  license="MIT",
  description="A minimal python example for gym-mujoco.",
  long_description=get_description(),
  long_description_content_type="text/markdown",
  packages=find_packages(exclude=["tests", "tests.*"]),
  package_data={"mjc_mwe": ["assets/*.xml"]},
  install_requires=[
    "gym",
    "mujoco",
  ],
  zip_safe=False,
  classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    "Development Status :: 3 - Alpha",
    # Indicate who your project is intended for
    "Intended Audience :: Science/Research",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # Pick your license as you wish (should match "license" above)
    "License :: OSI Approved :: MIT License",
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
  ],
)
