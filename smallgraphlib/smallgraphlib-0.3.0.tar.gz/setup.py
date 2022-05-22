# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smallgraphlib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'smallgraphlib',
    'version': '0.3.0',
    'description': 'Simple library for handling small graphs, including Tikz code generation.',
    'long_description': None,
    'author': 'Nicolas Pourcelot',
    'author_email': 'nicolas.pourcelot@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wxgeo/smallgraphlib',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
