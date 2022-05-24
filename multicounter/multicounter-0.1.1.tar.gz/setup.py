# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multicounter']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'multicounter',
    'version': '0.1.1',
    'description': 'A simple, elegant counter with support for counting multiple things at once.',
    'long_description': None,
    'author': 'Joseph Hale',
    'author_email': 'me@jhale.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
