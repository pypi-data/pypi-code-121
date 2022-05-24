# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylode']

package_data = \
{'': ['*'], 'pylode': ['rdf/*']}

install_requires = \
['Markdown>=3.3.7,<4.0.0', 'dominate>=2.6.0,<3.0.0', 'rdflib>=6.1.1,<7.0.0']

setup_kwargs = {
    'name': 'pylode',
    'version': '3.0.3',
    'description': '',
    'long_description': None,
    'author': 'Nicholas Car',
    'author_email': 'nick@kurrawong.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
