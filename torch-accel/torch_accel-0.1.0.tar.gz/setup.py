# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_accel']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.11.0,<2.0.0']

setup_kwargs = {
    'name': 'torch-accel',
    'version': '0.1.0',
    'description': '',
    'long_description': '# `torch_accel`\n\n',
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
