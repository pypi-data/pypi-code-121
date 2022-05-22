# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cecily']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cecily',
    'version': '0.1.1',
    'description': 'Minimalistic task queue using just the stdlib',
    'long_description': None,
    'author': 'Nick Yu',
    'author_email': 'nickyu42@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
