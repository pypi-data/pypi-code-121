# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['absolutely_nothing']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'absolutely-nothing',
    'version': '1.0.0',
    'description': 'A test module that does absolutely nothing.',
    'long_description': None,
    'author': 'Zach Taira',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
