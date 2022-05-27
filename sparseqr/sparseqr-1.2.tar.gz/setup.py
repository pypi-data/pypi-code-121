# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sparseqr']

package_data = \
{'': ['*']}

install_requires = \
['cffi>=1.0,<2.0', 'numpy>=1.21,<2.0', 'scipy>=1.0,<2.0']

setup_kwargs = {
    'name': 'sparseqr',
    'version': '1.2',
    'description': 'Python wrapper for SuiteSparseQR',
    'long_description': None,
    'author': 'Yotam Gingold',
    'author_email': 'yotam@yotamgingold.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
