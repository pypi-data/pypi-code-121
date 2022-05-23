# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_logs']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.2,<2.0.0', 'plotly>=5.8.0,<6.0.0', 'torch>=1.11.0,<2.0.0']

setup_kwargs = {
    'name': 'torch-logs',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'yohan-pg',
    'author_email': 'pg.yohan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
