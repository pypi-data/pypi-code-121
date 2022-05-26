# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bungio']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy[aiosqlite]>=1.4.36,<2.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'attrs>=21.4.0,<22.0.0']

extras_require = \
{'all': ['orjson>=3.6.8,<4.0.0',
         'aiodns>=3.0.0,<4.0.0',
         'cchardet>=2.1.7,<3.0.0',
         'Brotli>=1.0.9,<2.0.0',
         'aiohttp-client-cache>=0.7.0,<0.8.0',
         'mkdocstrings[python]>=0.18.1,<0.19.0',
         'mkdocs-material>=8.2.15,<9.0.0',
         'mkdocs-awesome-pages-plugin>=2.7.0,<3.0.0'],
 'cache': ['aiohttp-client-cache>=0.7.0,<0.8.0'],
 'docs': ['mkdocstrings[python]>=0.18.1,<0.19.0',
          'mkdocs-material>=8.2.15,<9.0.0',
          'mkdocs-awesome-pages-plugin>=2.7.0,<3.0.0'],
 'speedups': ['orjson>=3.6.8,<4.0.0',
              'aiodns>=3.0.0,<4.0.0',
              'cchardet>=2.1.7,<3.0.0',
              'Brotli>=1.0.9,<2.0.0']}

setup_kwargs = {
    'name': 'bungio',
    'version': '0.0.0',
    'description': 'A destiny 2 / bungie api wrapper',
    'long_description': '# BungIO\nWIP\n\n### Requirements\n-[x] Python 3.10+\n',
    'author': 'Daniel J',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kigstn/BungIO',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
