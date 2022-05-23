# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['polygon',
 'polygon.rest',
 'polygon.rest.models',
 'polygon.websocket',
 'polygon.websocket.models']

package_data = \
{'': ['*']}

install_requires = \
['certifi>=2021.10.8,<2022.0.0',
 'urllib3>=1.26.9,<2.0.0',
 'websockets>=10.3,<11.0']

setup_kwargs = {
    'name': 'polygon-api-client',
    'version': '1.0.0',
    'description': 'Official Polygon.io REST and Websocket client.',
    'long_description': None,
    'author': 'polygon.io',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://polygon.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
