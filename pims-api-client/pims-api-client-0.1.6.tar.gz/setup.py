# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pims_api_client', 'pims_api_client.methods', 'pims_api_client.schemas']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.22.0,<0.23.0',
 'pydantic>=1.9,<2.0',
 'pyhumps>=3.5.3,<4.0.0',
 'pytest-asyncio>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'pims-api-client',
    'version': '0.1.6',
    'description': 'INLB PIMS API Client',
    'long_description': None,
    'author': 'Никита Злаин',
    'author_email': 'nz@inlb.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.inlb.ru/inlb/python/pims-api-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
