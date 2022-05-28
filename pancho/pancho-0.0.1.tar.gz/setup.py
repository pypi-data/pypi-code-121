# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pancho']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pancho',
    'version': '0.0.1',
    'description': 'Commands processor',
    'long_description': None,
    'author': 'smairon',
    'author_email': 'man@smairon.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
