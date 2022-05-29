# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['terminalmuseum']

package_data = \
{'': ['*'], 'terminalmuseum': ['data/*']}

entry_points = \
{'console_scripts': ['APPLICATION-NAME = main:main']}

setup_kwargs = {
    'name': 'terminalmuseum',
    'version': '0.1.0',
    'description': 'TerminmalMuseum is a CLI Tool that displays a random piece of classical art onto your Terminal.',
    'long_description': None,
    'author': 'edincitaku',
    'author_email': 'edin.citaku@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
