#!/usr/bin/env python3

# standards
from pathlib import Path
import re

# 3rd parties
import setuptools


def get_version() -> str:
    version_file = Path(__file__).parent / 'hublot' / 'version.py'
    version_match = re.search(
        r"HUBLOT_VERSION = \'(.+)\'",
        version_file.read_text('UTF-8'),
    )
    if not version_match:
        raise Exception("Couldn't parse version.py")
    return version_match.group(1)


setuptools.setup(
    name='hublot',
    version=get_version(),
    description='A thin wrapper around Requests that adds caching and throttling',
    url='https://github.com/saintamh/hublot',
    author='Hervé Saint-Amand',
    packages=['hublot', 'hublot.cache'],
    package_data={'hublot': ['py.typed']},
    install_requires=[
        'dataclasses>=0.8,<1; python_version<"3.7"',
        'requests>=2.25,<3',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False, # https://mypy.readthedocs.io/en/latest/installed_packages.html#creating-pep-561-compatible-packages
)
