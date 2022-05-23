# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['thingsmatrix']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=12.0.1,<13.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['thingsmatrix = thingsmatrix.main:run']}

setup_kwargs = {
    'name': 'thingsmatrix',
    'version': '0.7.0',
    'description': '',
    'long_description': None,
    'author': 'yooooyo',
    'author_email': 'loipswqe@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
