# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiopayok', 'aiopayok.models']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aiopayok',
    'version': '0.1.0',
    'description': 'payok.io asynchronous python wrapper',
    'long_description': None,
    'author': 'layerqa',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/layerqa/aiopayok',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
