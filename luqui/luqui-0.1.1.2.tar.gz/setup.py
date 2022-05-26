# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['luqui']

package_data = \
{'': ['*']}

install_requires = \
['GromacsWrapper>=0.8.1,<0.9.0',
 'attrs>=21.4.0,<22.0.0',
 'pdb2pqr>=3.5.0,<4.0.0',
 'scipy>=1.7,<2.0',
 'toml>=0.10.1,<0.11.0']

setup_kwargs = {
    'name': 'luqui',
    'version': '0.1.1.2',
    'description': '',
    'long_description': None,
    'author': 'pgbarletta',
    'author_email': 'pbarletta@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
