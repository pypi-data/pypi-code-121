# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src']

package_data = \
{'': ['*']}

install_requires = \
['azure-identity>=1.10.0,<2.0.0',
 'azure-keyvault-secrets>=4.4.0,<5.0.0',
 'pymongo>=4.1.1,<5.0.0']

setup_kwargs = {
    'name': 'epomatti-aksmrc-core',
    'version': '0.1.4',
    'description': 'Shared code for my multi region AKS cluster microservices.',
    'long_description': None,
    'author': 'Evandro Pomatti',
    'author_email': 'evandro.pomatti@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/epomatti/azure-multiregion-aks-cluster',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
