# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mistql']

package_data = \
{'': ['*']}

install_requires = \
['lark>=1.0.0,<2.0.0', 'typeguard>=2.13.3,<3.0.0']

entry_points = \
{'console_scripts': ['mqpy = mistql.cli:main']}

setup_kwargs = {
    'name': 'mistql',
    'version': '0.4.11',
    'description': 'Python implementation of MistQL query language',
    'long_description': None,
    'author': 'Evin Sellin',
    'author_email': 'evinism@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
