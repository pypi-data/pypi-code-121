# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['service', 'service.ext', 'service.log', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['Babel==2.10.1',
 'Faker>=13.11.1,<14.0.0',
 'PyYAML>=6.0,<7.0',
 'Pygments>=2.12.0,<3.0.0',
 'fastapi>=0.78.0,<0.79.0',
 'fire>=0.4.0,<0.5.0',
 'httpx==0.22.0',
 'jsonrpcserver>=5.0.7,<6.0.0',
 'logging-json>=0.2.1,<0.3.0',
 'pytest-asyncio==0.18.3',
 'pytest-logger>=0.5.1,<0.6.0',
 'pytest>=7.1.2,<8.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.27.1,<3.0.0',
 'sentry-sdk==1.5.10',
 'tblib>=1.7.0,<2.0.0',
 'toml==0.10.2',
 'uvicorn>=0.17.6,<0.18.0',
 'yarl>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'pbt-service',
    'version': '5.0.0',
    'description': 'PortalBilet service core',
    'long_description': None,
    'author': 'everhide',
    'author_email': 'i.tolkachnikov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
