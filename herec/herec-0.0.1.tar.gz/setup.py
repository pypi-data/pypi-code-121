# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['herec']

package_data = \
{'': ['*']}

install_requires = \
['pyzmq>=23.0.0,<24.0.0']

setup_kwargs = {
    'name': 'herec',
    'version': '0.0.1',
    'description': 'Actor Implementation in Python built with ZeroMQ',
    'long_description': '# Herec\n Actor Implementation in Python built on ZeroMQ\n',
    'author': 'Ian Kollipara',
    'author_email': 'ian.kollipara@cune.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
