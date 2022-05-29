# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fdpy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fdpy',
    'version': '0.2.0',
    'description': 'fd wrapper for Python',
    'long_description': None,
    'author': 'Alyetama',
    'author_email': '56323389+Alyetama@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
