# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sc2', 'sc2.dicts', 'sc2.ids']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'loguru>=0.6.0,<0.7.0',
 'mpyq>=0.2.5,<0.3.0',
 'numpy>=1.19.3,<2.0.0',
 'portpicker>=1.4.0,<2.0.0',
 'protobuf<4.0.0',
 's2clientprotocol>=5.0.7,<6.0.0',
 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'burnysc2',
    'version': '6.0.2',
    'description': 'A StarCraft II API Client for Python 3',
    'long_description': None,
    'author': 'BurnySc2',
    'author_email': 'gamingburny@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Burnysc2/python-sc2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
