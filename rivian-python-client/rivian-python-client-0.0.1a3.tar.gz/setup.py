# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rivian']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.0.0', 'yarl>=1.6.0']

setup_kwargs = {
    'name': 'rivian-python-client',
    'version': '0.0.1a3',
    'description': 'Rivian API Client (Unofficial)',
    'long_description': None,
    'author': 'Brian Retterer',
    'author_email': 'bretterer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
