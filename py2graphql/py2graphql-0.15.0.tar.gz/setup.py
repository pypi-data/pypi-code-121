# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py2graphql']

package_data = \
{'': ['*']}

install_requires = \
['addict>=2.2.1,<3.0.0',
 'aiohttp>=3.6.2,<4.0.0',
 'requests>=2.24.0,<3.0.0',
 'tenacity>=6.2.0,<7.0.0']

setup_kwargs = {
    'name': 'py2graphql',
    'version': '0.15.0',
    'description': 'Pythonic GraphQL Client',
    'long_description': None,
    'author': 'Willem Thiart',
    'author_email': 'himself@willemthiart.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
