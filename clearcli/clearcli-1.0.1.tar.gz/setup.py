# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clearcli']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'clearcli',
    'version': '1.0.1',
    'description': 'Build Command Line Interface with ease',
    'long_description': '# ClearCLI\nBuild command line tool with ease\n',
    'author': 'Thomas Mahé',
    'author_email': 'contact@tmahe.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thmahe/clearcli',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
