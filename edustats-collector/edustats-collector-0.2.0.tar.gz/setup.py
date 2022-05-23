# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['result_collector_client']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'edustats-collector',
    'version': '0.2.0',
    'description': 'edustats collector client',
    'long_description': None,
    'author': 'Nicola Jordan',
    'author_email': 'njordan.hsr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
