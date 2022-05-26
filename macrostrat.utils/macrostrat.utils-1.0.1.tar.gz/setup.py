# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['macrostrat', 'macrostrat.utils']

package_data = \
{'': ['*']}

install_requires = \
['colorlog>=6.5.0,<7.0.0']

setup_kwargs = {
    'name': 'macrostrat.utils',
    'version': '1.0.1',
    'description': 'Core utilities for Sparrow',
    'long_description': None,
    'author': 'Daven Quinn',
    'author_email': 'dev@davenquinn.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
