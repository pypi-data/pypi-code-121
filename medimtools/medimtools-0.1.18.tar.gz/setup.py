#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()


# with open('requirements.txt') as req_file:
#     requirements = [line.rstrip() for line in req_file]

requirements = ["Click>7"]

test_requirements = ["pytest>=3"]

setup(
    author="Suraj Pai",
    author_email="b.pai@maastrichtuniversity.nl",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    entry_points={"console_scripts": ["medimtools=medimtools.cli:main"]},
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="medimtools",
    name="medimtools",
    packages=find_packages(include=["medimtools", "medimtools.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/surajpaib/medimtools",
    version="0.1.18",
    zip_safe=False,
)
