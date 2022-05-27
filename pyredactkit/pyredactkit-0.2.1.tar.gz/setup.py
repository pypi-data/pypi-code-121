# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyredactkit']

package_data = \
{'': ['*']}

install_requires = \
['nltk>=3.7,<4.0', 'numpy<1.22.0']

entry_points = \
{'console_scripts': ['pyredactkit = pyredactkit.pyredactkit:main',
                     'pyredactor = pyredactkit.pyredactkit:main']}

setup_kwargs = {
    'name': 'pyredactkit',
    'version': '0.2.1',
    'description': 'Python cli tool to redact sensitive data',
    'long_description': None,
    'author': 'brootware',
    'author_email': 'brootware@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/brootware/PyRedactKit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
