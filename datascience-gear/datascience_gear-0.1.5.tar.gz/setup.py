# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datascience_gear']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'datascience-gear',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'sinclairfr',
    'author_email': 'sixfoursuited@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
