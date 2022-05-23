#!/usr/bin/python3

import feii
from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = [
    "requests>=2",
    "click",
]

setup(
  name = "feii",
  version = feii.__version__,
  author = "Anton Turko",
  author_email = "anton_turko@mail.ru",
  url = "https://github.com/antohhh93/feii",
  description = "Fix error ilm index in Elasticsearch",
  long_description = readme,
  long_description_content_type = "text/markdown",
  packages = find_packages(),
  install_requires = requirements,
  license = "MIT",
  classifiers = [
      "Programming Language :: Python :: Implementation",
      "Programming Language :: Python :: 3",
      "Natural Language :: English",
      "License :: OSI Approved :: MIT License"
  ],
  entry_points = {
    "console_scripts": [
        "feii = feii.cli:cli",
    ],
  },
)
