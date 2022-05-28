# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wizdiff']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'click>=8.0.1,<9.0.0',
 'loguru>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'wizdiff',
    'version': '0.2.1',
    'description': 'wizard101 version diffing automation tool',
    'long_description': None,
    'author': 'StarrFox',
    'author_email': 'starrfox6312@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
