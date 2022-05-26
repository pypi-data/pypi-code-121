# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redshift_data_api']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.38,<2.0.0', 'pandas>=1.2.3,<2.0.0']

setup_kwargs = {
    'name': 'redshift-data-api',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Giacomo Tagliabue',
    'author_email': 'giacomo.tag@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
