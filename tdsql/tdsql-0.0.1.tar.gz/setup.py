# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdsql', 'tdsql.client']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pandas>=1.4.2,<2.0.0']

extras_require = \
{'bigquery': ['google-cloud-bigquery>=3.1.0,<4.0.0', 'db-dtypes>=1.0.1,<2.0.0']}

entry_points = \
{'console_scripts': ['tdsql = tdsql.command:main']}

setup_kwargs = {
    'name': 'tdsql',
    'version': '0.0.1',
    'description': 'Minimum test flamework for sql',
    'long_description': None,
    'author': 'dr666m1',
    'author_email': 'skndr666m1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
