# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nextup']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0']

setup_kwargs = {
    'name': 'nextup',
    'version': '0.1.0',
    'description': 'Next Up your Next Install',
    'long_description': None,
    'author': 'VincentRPS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
