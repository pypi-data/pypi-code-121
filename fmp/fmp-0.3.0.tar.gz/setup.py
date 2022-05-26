# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fmp']

package_data = \
{'': ['*']}

install_requires = \
['autoflake>=1.4,<2.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=10.11.0,<11.0.0',
 'yapf>=0.32.0,<0.33.0']

entry_points = \
{'console_scripts': ['fmp = fmp:cli.main']}

setup_kwargs = {
    'name': 'fmp',
    'version': '0.3.0',
    'description': 'Formats python files with properly sorted import statemnts',
    'long_description': None,
    'author': 'Alyetama',
    'author_email': '56323389+Alyetama@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
