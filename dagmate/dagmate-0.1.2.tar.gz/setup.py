# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dagmate']

package_data = \
{'': ['*']}

install_requires = \
['dagit>=0.14.13,<0.15.0',
 'dagster-graphql>=0.14.13,<0.15.0',
 'dagster>=0.14.13,<0.15.0',
 'protobuf>=3.20.1,<3.21.0']

setup_kwargs = {
    'name': 'dagmate',
    'version': '0.1.2',
    'description': 'Make your Dagster deployment faster and easier with Dagmate',
    'long_description': None,
    'author': 'Anoop Sharma',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
