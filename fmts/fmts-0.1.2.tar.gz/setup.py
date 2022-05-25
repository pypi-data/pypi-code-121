# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['fmts']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fmts',
    'version': '0.1.2',
    'description': 'str transformation utils',
    'long_description': '<a href="https://github.com/dynamic-graphics-inc/dgpy-libs">\n<img align="right" src="https://github.com/dynamic-graphics-inc/dgpy-libs/blob/main/docs/images/dgpy_banner.svg?raw=true" alt="drawing" height="120" width="300"/>\n</a>\n\n# fmts\n\n[![Wheel](https://img.shields.io/pypi/wheel/fmts.svg)](https://img.shields.io/pypi/wheel/fmts.svg)\n[![Version](https://img.shields.io/pypi/v/fmts.svg)](https://img.shields.io/pypi/v/fmts.svg)\n[![py_versions](https://img.shields.io/pypi/pyversions/fmts.svg)](https://img.shields.io/pypi/pyversions/fmts.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n**Install:** `pip install fmts` OR `poetry add fmts`\n\n**What:** typed & tested python itertools/generators-utils library\n',
    'author': 'jesse',
    'author_email': 'jesse@dgi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dynamic-graphics-inc/dgpy-libs/tree/main/libs/fmts',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
