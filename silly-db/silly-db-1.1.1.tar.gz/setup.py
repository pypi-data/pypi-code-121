#! /usr/bin/env python3
# coding: utf-8

"""
This file only belongs to pypi setup, not with silly_db in itself.

REMINDER:
1- build
./setup.py sdist bdist_wheel
2- basic verifications
twine check dist/*
2.5- Deploy on testpypi (optionnal, site here : https://test.pypi.org/):
twine upload --repository testpypi dist/*
3- upload to PyPi
twine upload dist/*
"""

from silly_db import __version__
import pathlib
from setuptools import setup


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="silly-db",
    version=f"{__version__}",
    description=(
        "Very light ORM for SQLite, simple and efficient"
        ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/byoso/silly_db",
    author="Vincent Fabre",
    author_email="peigne.plume@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    packages=[
        "silly_db",
        "silly_db.plop",
        "silly_db.plop.db",
        "silly_db.plop.db.database",
        "silly_db.plop.db.database.migrations",
        ],
    # include_package_data=True,
    package_data={'': ['*.sql', '*.txt']},
    python_requires='>=3.6',
    # install_requires=[],
    keywords='database sqlite3 sqlite db orm',
    entry_points={
        "console_scripts": [
            "realpython=silly_db.__main__:main",
        ]
    },
    setup_requires=['wheel'],
)
