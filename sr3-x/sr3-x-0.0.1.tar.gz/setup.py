# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sr3_x', 'sr3_x.models', 'sr3_x.models.unet']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.11.0,<2.0.0']

setup_kwargs = {
    'name': 'sr3-x',
    'version': '0.0.1',
    'description': 'An implementation of SR3 from Google',
    'long_description': None,
    'author': 'paulcjh',
    'author_email': 'paulcjh@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
