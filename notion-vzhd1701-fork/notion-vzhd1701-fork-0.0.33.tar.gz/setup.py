# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notion']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'cached-property>=1.5.2,<2.0.0',
 'commonmark>=0.9.1,<0.10.0',
 'dictdiffer>=0.9.0,<0.10.0',
 'python-slugify>=6.1.2,<7.0.0',
 'requests>=2.27.1,<3.0.0',
 'tzlocal>=4.2,<5.0']

setup_kwargs = {
    'name': 'notion-vzhd1701-fork',
    'version': '0.0.33',
    'description': 'Fork of https://github.com/jamalex/notion-py',
    'long_description': None,
    'author': 'Jamie Alexandre',
    'author_email': 'jamalex@gmail.com',
    'maintainer': 'vzhd1701',
    'maintainer_email': 'vzhd1701@gmail.com',
    'url': 'https://github.com/vzhd1701/notion-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
