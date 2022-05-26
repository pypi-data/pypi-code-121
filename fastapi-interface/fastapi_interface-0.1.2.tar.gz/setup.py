# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fastapi_interface', 'fastapi_interface.schemas', 'fastapi_interface.views']

package_data = \
{'': ['*']}

install_requires = \
['edulib',
 'email-validator>=1.2.1,<2.0.0',
 'fastapi>=0.78.0,<0.79.0',
 'orjson>=3.6.8,<4.0.0',
 'python-jose[cryptography]>=3.3.0,<4.0.0',
 'python-multipart>=0.0.5,<0.0.6']

setup_kwargs = {
    'name': 'fastapi-interface',
    'version': '0.1.2',
    'description': 'for DRY in microservices',
    'long_description': 'None',
    'author': 'koevgeny10',
    'author_email': 'koevgeny10@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
