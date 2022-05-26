#!/usr/bin/env python
"""setup.py for cmemc."""

from setuptools import setup, find_packages

setup(
    name="cmem_cmemc",
    version="22.1",
    author="eccenca",
    author_email="cmempy-developer@eccenca.com",
    maintainer="Sebastian Tramp",
    maintainer_email="sebastian.tramp@eccenca.com",
    url="https://eccenca.com/go/cmemc",
    description="Command line client for eccenca Corporate Memory",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license="Apache 2.0",
    entry_points={
        "console_scripts": [
            "cmemc = cmem.cmemc.cli:main",
        ],
    },
    install_requires=[
        "certifi",
        "click==7.1.2",
        "click_help_colors",
        "click-didyoumean",
        "configparser",
        "Jinja2",
        "natsort",
        "Pygments",
        "pyjwt",
        "requests",
        "tabulate",
        "timeago",
        "treelib",
        "urllib3",
        "six",
        "prometheus_client",
        "requests_toolbelt",
        # need to be freezed for release
        "cmem-cmempy==22.1"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Testing",
        "Topic :: Database",
        "Topic :: Utilities",
    ],
)
