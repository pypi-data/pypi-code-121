# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_loops']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'torch-loops',
    'version': '0.3.0',
    'description': 'simple loops for pytorch',
    'long_description': None,
    'author': 'yohan-pg',
    'author_email': 'pg.yohan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
