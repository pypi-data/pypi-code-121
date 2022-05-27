# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_chargepoint']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'python-chargepoint',
    'version': '1.3.0',
    'description': 'A simple, Pythonic wrapper for the ChargePoint API.',
    'long_description': None,
    'author': 'Marc Billow',
    'author_email': 'mbillow@users.noreply.github.compoetry',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
