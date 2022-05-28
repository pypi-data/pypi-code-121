# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['detapack']

package_data = \
{'': ['*']}

install_requires = \
['deta>=1.1.0,<2.0.0', 'progress>=1.6,<2.0', 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['detapack = detapack.main:app']}

setup_kwargs = {
    'name': 'detapack',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Paul Haedrich',
    'author_email': 'paul@berrysauce.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
