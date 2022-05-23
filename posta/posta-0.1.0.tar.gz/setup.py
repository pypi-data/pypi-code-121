# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['posta']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'posta',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'seifashraf1',
    'author_email': 'seifsefo50@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
