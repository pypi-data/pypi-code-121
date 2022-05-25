# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kripta_py']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodome>=3.14.1,<4']

setup_kwargs = {
    'name': 'kripta-py',
    'version': '0.1.0',
    'description': 'A tiny asymmetric/symmetric ecnryption lib for humans.',
    'long_description': None,
    'author': 'sanix-darker',
    'author_email': 's4nixd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
