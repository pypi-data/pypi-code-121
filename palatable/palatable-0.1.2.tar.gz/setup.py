#!/usr/bin/env python
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="palatable",
    version="0.1.2",
    packages=["palatable"],
    install_requires=["Faker==13.11.1", "tabulate==0.8.9"],
    entry_points={
        "console_scripts": [
            "palatable = palatable.scheduler:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Software Development",
    ],
    url="https://github.com/iamjazzar/palatable",
    license="GNU Affero General Public License v3",
    author="Ahmed Jazzar",
    author_email="me@ahmedjazzar.com",
    description="Fast, reliable exams scheduler",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
