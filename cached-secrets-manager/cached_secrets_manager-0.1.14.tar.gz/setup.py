# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cached_secrets_manager']

package_data = \
{'': ['*']}

install_requires = \
['boto3==1.23.9', 'botocore>=1.26.10,<2.0.0']

setup_kwargs = {
    'name': 'cached-secrets-manager',
    'version': '0.1.14',
    'description': '',
    'long_description': None,
    'author': 'Maximilian Walther',
    'author_email': 'max@spryfox.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.12,<4.0.0',
}


setup(**setup_kwargs)
