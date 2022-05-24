# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['example_cli']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'example-cli',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'RincewindWizzard',
    'author_email': 'git@magierdinge.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
