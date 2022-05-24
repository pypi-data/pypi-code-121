# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uploadcare']

package_data = \
{'': ['*']}

install_requires = \
['dateparser>=1.1.1,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'uploadcare',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Alyetama',
    'author_email': '56323389+Alyetama@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
