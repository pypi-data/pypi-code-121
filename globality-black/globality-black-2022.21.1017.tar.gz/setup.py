#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

project = "globality-black"
version = "2022.21.1017"

setup(
    name=project,
    author="Globality AI",
    version=version,
    author_email="ai@globality.com",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A wrapper for black adding new features",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    url="https://github.com/globality-corp/globality-black",
    keywords="globality_black",
    entry_points={
        "console_scripts": [
            "globality-black = globality_black.cli:main",
        ],
    },
    install_requires=[
        "Click>=7.0,<8.0",
        # TODO: remove tomli pinning when black version is changed to 22.x
        "tomli<2.0.0",
        "parso",
        "pytest>=3",
        "black==21.7b0",
        "pexpect",
    ],
    extras_require={
        "jupyter": [
            "jupyterlab-code-formatter",
        ],
        "lint": [
            "flake8-isort>=3.0.1",
            "flake8-print>=3.1.0",
            "flake8-logging-format",
            "globality-black",
        ],
        "typehinting": [
            "mypy",
            "types-setuptools",
        ],
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },
    include_package_data=True,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    test_suite="tests",
    zip_safe=False,
)
