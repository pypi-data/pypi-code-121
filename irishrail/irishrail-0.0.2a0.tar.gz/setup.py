# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['irishrail', 'irishrail.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'httpx>=0.23.0,<0.24.0',
 'rich>=12.4.4,<13.0.0',
 'xmltodict>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['irishrail = irishrail.cli:cli']}

setup_kwargs = {
    'name': 'irishrail',
    'version': '0.0.2a0',
    'description': '',
    'long_description': None,
    'author': 'Marco Rougeth',
    'author_email': 'rougeth@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
