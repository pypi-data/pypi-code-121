# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clj']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'clj',
    'version': '0.3.0',
    'description': 'Utilities for lazy iterables',
    'long_description': None,
    'author': 'Baptiste Fontaine',
    'author_email': 'b@ptistefontaine.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
