# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multisig_ci']

package_data = \
{'': ['*']}

install_requires = \
['ape_safe==0.5.0',
 'eth_brownie==1.17',
 'gnosis-py==3.6.0',
 'psutil==5.8.0',
 'requests==2.26.0',
 'tenacity==8.0.1']

setup_kwargs = {
    'name': 'multisig-ci',
    'version': '0.2.0',
    'description': 'Gnosis safe ci scripts.',
    'long_description': None,
    'author': 'kx9x',
    'author_email': 'kx9x@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
