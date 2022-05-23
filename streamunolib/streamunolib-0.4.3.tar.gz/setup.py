# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamunolib']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'streamunolib',
    'version': '0.4.3',
    'description': 'Library of generic transform components.',
    'long_description': None,
    'author': 'Pierre Chanial',
    'author_email': 'pierre.chanial@apc.in2p3.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
