# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['two_tables']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0', 'openpyxl>=3.0.10,<4.0.0']

entry_points = \
{'console_scripts': ['two_tables = two_tables.updater:main']}

setup_kwargs = {
    'name': 'two-tables',
    'version': '0.1.2',
    'description': 'Automatically update two tables',
    'long_description': None,
    'author': 'LilyWhite',
    'author_email': 'lilywhite2005@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
