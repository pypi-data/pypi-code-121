# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eve_client']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl==1.4.0', 'python-dateutil==2.8.2', 'requests==2.26.0']

setup_kwargs = {
    'name': 'eve-client',
    'version': '1.0.0',
    'description': 'EVE API client from Exodus Intelligence LLC.',
    'long_description': 'None',
    'author': 'DevTeam',
    'author_email': 'dev@exodusintel.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
