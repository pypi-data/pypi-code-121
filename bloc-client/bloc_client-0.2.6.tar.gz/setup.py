# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bloc_client', 'bloc_client.internal']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.21.1,<0.22.0', 'pika>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'bloc-client',
    'version': '0.2.6',
    'description': 'python client sdk for bloc',
    'long_description': None,
    'author': 'pillipanda',
    'author_email': 'pillipanda@126.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
