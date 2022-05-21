# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['istars']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'istars',
    'version': '0.0.0',
    'description': '',
    'long_description': None,
    'author': 'Alex Rudolph',
    'author_email': 'alex3rudolph@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
