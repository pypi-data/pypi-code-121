# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiopayok', 'aiopayok.models']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'certifi>=2022.5.18,<2023.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'aiopayok',
    'version': '0.1.2',
    'description': 'payok.io asynchronous python wrapper',
    'long_description': '# aiopayok\npayok.io asynchronous python wrapper\n',
    'author': 'layerqa',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/layerqa/aiopayok',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
