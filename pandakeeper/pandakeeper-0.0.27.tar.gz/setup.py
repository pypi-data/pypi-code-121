# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pandakeeper',
 'pandakeeper.dataloader',
 'pandakeeper.dataloader.sql',
 'pandakeeper.dataprocessor']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1,<2',
 'pandera>=0.9',
 'typing-extensions>=4',
 'varname>=0.8,<0.9',
 'varutils>=0.0.8,<0.0.9']

setup_kwargs = {
    'name': 'pandakeeper',
    'version': '0.0.27',
    'description': 'Python library designed to simplify the validation of dataset manipulations.',
    'long_description': '# pandakeeper\nPython library designed to simplify the validation of dataset manipulations.\n',
    'author': 'Andrew Sonin',
    'author_email': 'sonin.cel@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrewsonin/pandakeeper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
