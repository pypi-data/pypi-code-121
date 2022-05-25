# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dubletten_tool',
 'dubletten_tool.management',
 'dubletten_tool.management.commands',
 'dubletten_tool.migrations']

package_data = \
{'': ['*'], 'dubletten_tool': ['static/dubletten_tool/css/*', 'templates/*']}

install_requires = \
['python-Levenshtein>=0.12.2,<0.13.0']

setup_kwargs = {
    'name': 'dubletten-tool',
    'version': '0.1.6',
    'description': 'APIS module for the VieCPro instance to perform manual deduplication of person instances',
    'long_description': None,
    'author': 'Gregor Pirgie',
    'author_email': 'gregor.pirgie@oeaw.ac.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
