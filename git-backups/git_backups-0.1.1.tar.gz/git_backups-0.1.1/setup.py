#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

try:
    with open("HISTORY.rst") as history_file:
        history = history_file.read()
except IOError:
    history = ""

requirements = []

test_requirements = [
    "pytest>=7",
]

setup(
    author="Kedar Deore",
    author_email="kedardeore@gmail.com",
    python_requires=">=3.7,<3.10",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Backup git repositories to a Gitlab instance",
    entry_points={
        "console_scripts": [
            "gitbak=git_backups.main:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="git_backups",
    name="git_backups",
    packages=find_packages(include=["src/git_backups", "src/git_backups.*"]),
    package_dir={"": "src/git_backups"},
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/0xKD/gitbackups",
    version="0.1.1",
    zip_safe=False,
)
