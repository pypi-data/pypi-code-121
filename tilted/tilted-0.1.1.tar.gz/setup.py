# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tilted']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tilted',
    'version': '0.1.1',
    'description': 'Tilted is a lightweight, open-source Python package with a simple interface for poker hand evaluation & comparison.',
    'long_description': None,
    'author': 'Max Atkinson',
    'author_email': 'hiremaxatkinson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
