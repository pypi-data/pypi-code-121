# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['detapack']

package_data = \
{'': ['*']}

install_requires = \
['deta>=1.1.0,<2.0.0', 'progress>=1.6,<2.0', 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['detapack = detapack.main:app']}

setup_kwargs = {
    'name': 'detapack',
    'version': '0.1.2',
    'description': '',
    'long_description': '<h1 align="center">detapack 📄</h1>\n<p align="center"><strong>Import/Export data from/to Deta Bases</strong></p>\n<p align="center">\n    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/detapack">\n    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/detapack">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/detapack">\n    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/berrysauce/detapack">\n</p>\n\n## What is detapack?\ndetapack is a tiny & simple CLI built with [Typer](https://github.com/tiangolo/typer) (in Python) which can import and export data from and to Deta Bases.\n\n## How to install detapack?\ndetapack can be installed the Python Package Index.\n```\npip install detapack\n```\nRun `detapack version` to check if detapack was installed successfully. You may need to add detapack to your shell configuration.',
    'author': 'Paul Haedrich',
    'author_email': 'paul@berrysauce.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
