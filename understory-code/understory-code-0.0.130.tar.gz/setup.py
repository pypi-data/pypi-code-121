# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory', 'understory.code']

package_data = \
{'': ['*'], 'understory.code': ['templates/*']}

install_requires = \
['understory>=0.0,<0.1', 'warez>=0.0,<0.1']

entry_points = \
{'understory': ['code = understory.code:app']}

setup_kwargs = {
    'name': 'understory-code',
    'version': '0.0.130',
    'description': 'Host code in the understory',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ragt.ag/code/understory-code',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
