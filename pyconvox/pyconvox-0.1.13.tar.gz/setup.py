#!/usr/bin/env python
import codecs
import os.path
import re
import sys

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = []


setup_options = dict(
    name='pyconvox',
    version=find_version("pyconvox", "__version__.py"),
    description='Universal Command Line Environment for Pyconvox, a wrapper for convox application.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(include=[
        'pyconvox', 'pyconvox.*',
    ]),
    entry_points={
        'console_scripts': [
            'pyconvox = pyconvox.__main__:main'
        ],
    },
    include_package_data=True,
    author='ABHINAVKISHOREGV',
    author_email='kishorebolt60@gmail.com',
    license="MIT License",
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
    ),
)

setup(**setup_options)
