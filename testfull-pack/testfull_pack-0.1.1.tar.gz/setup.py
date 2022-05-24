# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['testfull_pack']

package_data = \
{'': ['*']}

install_requires = \
['logsmal>=0.0.9,<0.0.10', 'pytest>=7.1.1,<8.0.0']

setup_kwargs = {
    'name': 'testfull-pack',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Denis Kustov',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
