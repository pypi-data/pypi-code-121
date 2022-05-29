# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['polisher', 'polisher.displayer', 'polisher.tests']

package_data = \
{'': ['*']}

install_requires = \
['plotly>=5.8.0,<6.0.0']

setup_kwargs = {
    'name': 'polisher',
    'version': '2.0.2',
    'description': 'Graph polisher is a library that helps you clean your plotly figures.',
    'long_description': None,
    'author': 'Rodrigo da Silva',
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
