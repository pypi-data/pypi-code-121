# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['peb']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'peb',
    'version': '0.0.6',
    'description': 'Python Extensions Bundle',
    'long_description': '# PEB\n\nPEB is Python Extensions Bundle.',
    'author': 'Jrog',
    'author_email': 'jrog612@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jrog612/djackal',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
