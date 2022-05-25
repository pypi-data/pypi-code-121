#!/usr/bin/env python3
"""Setup script for ITS Private Cloud CLI."""
import codecs
from datetime import datetime as dt
import os
import re
from typing import List

from setuptools import find_packages, setup

# shared consts using approach suggested at
# https://stackoverflow.com/questions/17583443/what-is-the-correct-way-to-share-package-version-with-setup-py-and-the-package


def read(*parts):
    """Read file from current directory."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'r') as infofile:
        return infofile.read()


def find_version(*file_paths):
    """Locate version info to share between const.py and setup.py."""
    version_file = read(*file_paths)  # type: ignore
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def load_requirements(requires_file: str = 'requirements.txt') -> List[str]:
    """Load requirements from file"""
    reqs = []
    with open(requires_file, encoding='utf-8') as f:
        _lines = f.read().splitlines()
    for line in _lines:
        line = line.strip('\n')
        if not line.startswith('#') and line != '':
            reqs.append(line)
    return reqs


__VERSION__ = find_version("vss_cli", "const.py")  # type: ignore

REQUIRED_PYTHON_VER = (3, 7, 5)
REQUIRES = load_requirements()
# REQUIRES = [req for req in INSTALL_REQUIRES if req and not re.match(r'[^:]+://', req)]

PACKAGES = find_packages(exclude=['tests', 'tests.*'])
PACKAGE_DATA = {'vss_cli': ['data/*.yaml']}

PROJECT_NAME = 'ITS Private Cloud CLI'
PROJECT_PACKAGE_NAME = 'vss-cli'
PROJECT_LICENSE = 'MIT'
PROJECT_AUTHOR = 'University of Toronto'
PROJECT_COPYRIGHT = f' 2019-{dt.now().year}, {PROJECT_AUTHOR}'
PROJECT_URL = 'https://gitlab-ee.eis.utoronto.ca/vss/vss-cli'
PROJECT_DOCS = 'https://eis.utoronto.ca/~vss/vss-cli'
PROJECT_EMAIL = 'vss-apps@eis.utoronto.ca'
MAINTAINER_EMAIL = 'vss-py@eis.utoronto.ca'

PROJECT_GITLAB_GROUP = 'vss'
PROJECT_GITLAB_REPOSITORY = 'vss-cli'

PYPI_URL = f'https://pypi.python.org/pypi/{PROJECT_PACKAGE_NAME}'
GITLAB_PATH = f'{PROJECT_GITLAB_GROUP}/{PROJECT_GITLAB_REPOSITORY}'
GITLAB_URL = f'https://gitlab-ee.eis.utoronto.ca/{GITLAB_PATH}'

DOWNLOAD_URL = f'{GITLAB_URL}/archive/{__VERSION__}.zip'
PROJECT_URLS = {
    'Bug Reports': f'{GITLAB_URL}/issues',
    'Documentation': f'{PROJECT_DOCS}/',
    'Source': f'{PROJECT_URL}',
}
STOR_REQUIRE = ['minio==7.1.5']
TESTS_REQUIRE = [
    'flake8==4.0.1',
    'nose==1.3.7',
    'coverage==6.0.2',
    'pytz==2021.3',
    'wheel==0.37.0',  # Otherwise setup.py bdist_wheel does not work
    *STOR_REQUIRE,
]
DEV_REQUIRE = [
    *TESTS_REQUIRE,
    *STOR_REQUIRE,
    'sphinx-rtd-theme==1.0.0',
    'Sphinx==4.2.0',
]

# Allow you to run
# pip install .[test]
# pip install .[dev]
# to get test dependencies included
EXTRAS_REQUIRE = {
    'test': TESTS_REQUIRE,
    'dev': DEV_REQUIRE,
    'stor': STOR_REQUIRE,
}

MIN_PY_VERSION = '.'.join(map(str, REQUIRED_PYTHON_VER))


setup(
    name=PROJECT_PACKAGE_NAME,
    version=__VERSION__,
    url=PROJECT_URL,
    download_url=DOWNLOAD_URL,
    project_urls=PROJECT_URLS,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    maintainer_email=MAINTAINER_EMAIL,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    license=PROJECT_LICENSE,
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require=EXTRAS_REQUIRE,
    python_requires=f'>={MIN_PY_VERSION}',
    entry_points={
        'console_scripts': [
            'vss-cli = vss_cli.cli:run',
            'vss = vss_cli.cli:run',
        ]
    },
)
