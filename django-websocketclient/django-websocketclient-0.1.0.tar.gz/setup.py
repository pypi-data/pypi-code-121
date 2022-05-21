# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['websocketclient',
 'websocketclient.management',
 'websocketclient.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0.4,<5.0.0', 'websockets>=10.3,<11.0']

setup_kwargs = {
    'name': 'django-websocketclient',
    'version': '0.1.0',
    'description': 'A persistent websocket client for Django',
    'long_description': None,
    'author': 'Kiran Kumbhar',
    'author_email': 'kiranpk189@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
