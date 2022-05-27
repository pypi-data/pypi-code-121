# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nops_metadata', 'nops_metadata.tests']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.102', 'pyrsistent>=0.17.3']

setup_kwargs = {
    'name': 'nops-metadata',
    'version': '0.2.1',
    'description': 'Metadata producer tooling used in nOps.io',
    'long_description': None,
    'author': 'nOps Engineers',
    'author_email': 'eng@nops.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
