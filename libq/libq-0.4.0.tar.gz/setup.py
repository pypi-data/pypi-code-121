# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libq']

package_data = \
{'': ['*']}

install_requires = \
['hiredis>=2.0.0,<3.0.0',
 'nanoid>=2.0.0,<3.0.0',
 'orjson>=3.6.8,<4.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'redis>=4.3.1,<5.0.0',
 'rich>=12.4.1,<13.0.0']

setup_kwargs = {
    'name': 'libq',
    'version': '0.4.0',
    'description': 'Simple async and sync queue system',
    'long_description': None,
    'author': 'nuxion',
    'author_email': 'nuxion@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nuxion/libq',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
