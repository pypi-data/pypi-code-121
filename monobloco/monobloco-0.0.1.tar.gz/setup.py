# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['monobloco']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.15,<2.0', 'tqdm>=4.40.0,<5.0.0']

setup_kwargs = {
    'name': 'monobloco',
    'version': '0.0.1',
    'description': 'Minimalist interfaces for taca taca toco toco taca taca',
    'long_description': None,
    'author': 'don toco',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
