# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plot3d']

package_data = \
{'': ['*']}

install_requires = \
['numpy', 'pandas', 'scipy', 'tqdm']

setup_kwargs = {
    'name': 'plot3d',
    'version': '1.4.8',
    'description': 'Plot3D python utilities for reading and writing and also finding connectivity between blocks',
    'long_description': None,
    'author': 'Paht Juangphanich',
    'author_email': 'paht.juangphanich@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
