# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fluxpoint']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.2,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'fluxpoint',
    'version': '0.1.0',
    'description': 'A library for making interaction with the Fluxpoint API easy.',
    'long_description': None,
    'author': 'kunosyn',
    'author_email': 'kunosyn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<3.9',
}


setup(**setup_kwargs)
