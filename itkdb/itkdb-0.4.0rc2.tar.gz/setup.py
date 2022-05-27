#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import sys

if sys.version_info.major < 3:
    from io import open
with open(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md"),
    encoding="utf-8",
) as readme_md:
    long_description = readme_md.read()

extras_require = {
    "develop": [
        "flake8",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "coverage",
        "tbump>=6.7.0",
        "pre-commit",
        "bandit",
        'black;python_version>="3.6"',  # Black is Python3 only
        "betamax",  # recording api calls for testing
        "betamax-serializers",
        "twine",  # uploading to pypi
        "requests-mock",
    ],
    "plotting": ["matplotlib"],
}
extras_require["complete"] = sorted(set(sum(extras_require.values(), [])))


setup(
    name="itkdb",
    version="0.4.0rc2",
    use_scm_version=lambda: {"local_scheme": lambda version: ""},
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests"]),
    include_package_data=True,
    description="Python wrapper to interface with ITk DB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/atlas-itk/sw/db/itkdb",
    author="Giordon Stark",
    author_email="gstark@cern.ch",
    license="",
    keywords="physics itk database wrapper",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=1.6.1",  # for all HTTP calls to the API
        "certifi",  # SSL
        "cachecontrol[filecache]",  # for caching HTTP requests according to spec to local file
        "click>=6.0",  # for console scripts,
        "python-jose",  # for id token decoding
        "attrs",  # for model inflation/deflation
        "python-dotenv",  # for loading env variables
        "simple-settings",  # for handling settings more easily
        'importlib_resources; python_version < "3.9"',
        "python-magic",  # for getting the filetype
        "pylibmagic",  # for shipping the magic library for python-magic
    ],
    extras_require=extras_require,
    entry_points={"console_scripts": ["itkdb=itkdb.commandline:itkdb"]},
    dependency_links=[],
)
