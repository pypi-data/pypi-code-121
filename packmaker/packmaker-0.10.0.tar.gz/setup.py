#!/usr/bin/env python

import sys
if sys.version_info < (3, 5):
    sys.exit('Packmaker requires Python 3.5 or higher')

from setuptools import find_packages, setup

import os
try:
    packmaker_version = os.environ['PACKMAKER_VERSION']
except KeyError:
    import subprocess
    try:
        # try to build a PEP440 compatible version based on the output of
        # the git describe command
        def git_command(args):
            try:
                cmd = ['git', '-C', os.path.dirname(os.path.realpath(__file__))]
                return subprocess.check_output(cmd + args).decode().strip()
            except OSError as exc:
                sys.exit('No PACKMAKER_VERSION envvar defined and getting an error '
                         + 'running git to calculate the version\n{}'.format(exc))
        v_full = git_command(['describe', '--tags', '--dirty=.dirty'])
        v_tag = git_command(['describe', '--tags', '--abbrev=0'])
        v_tail = v_full[len(v_tag):]
        packmaker_version = v_tag + v_tail.replace('-', '.dev', 1).replace('-', '+', 1)
    except subprocess.CalledProcessError:
        packmaker_version = 'unknown'

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
  name='packmaker',
  version=packmaker_version,
  description='minecraft modpack maker',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='Mark Crewson',
  author_email='mark@crewson.net',
  url='https://packmaker.readthedocs.io',

  classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Topic :: Games/Entertainment",
  ],

  keywords='minecraft modded modpack',

  packages=find_packages(exclude=('tests',)),

  install_requires=[
    'aiohttp==3.7.3',
    'chardet==3.0.4',
    'jinja2',
    'prettytable',
    'python-dateutil',
    'pyyaml',
    'requests',
    'requests_cache',
    'urllib3',
  ],

  python_requires='>=3.6',

  entry_points={
    'console_scripts': [
        'packmaker = packmaker.main:main'
    ]
  }
)
