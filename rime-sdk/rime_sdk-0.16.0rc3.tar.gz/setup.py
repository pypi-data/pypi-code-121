"""Setup file for package."""

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("../../protos/python_requirements.txt") as f:
    proto_reqs = f.read().splitlines()

setup(
    name="rime_sdk",
    packages=find_packages(include=["rime_sdk*"]),
    description="Package to programmatically access a RIME deployment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # TODO(blaine): upgrade to semver 3 when it is released.
    setuptools_git_versioning={"enabled": True},
    setup_requires=["setuptools-git-versioning"],
    install_requires=[
        # Note: click is a dependency of `requests` but has to be pinned here
        # due to https://github.com/psf/black/issues/2964 .
        "click==8.0.1",
        "deprecated>=1.0.0,<2.0.0",
        "semver>=2.10.0,<3.0.0",
        "simplejson",
        "pandas>=1.1.0",
        "requests>=2.0.0",
        "tqdm",
        # below reqs are for data_format_check
        "schema",
        "numpy",
    ]
    + proto_reqs,
    python_requires=">=3.6",
    license="OSI Approved :: Apache Software License",
    entry_points={
        "console_scripts": [
            "rime-data-format-check=rime_sdk.data_format_check.cli:main",
        ]
    },
)
