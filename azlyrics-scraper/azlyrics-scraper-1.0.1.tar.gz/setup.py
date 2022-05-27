# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['azlyrics_scraper']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'azlyrics-scraper',
    'version': '1.0.1',
    'description': 'Search for artists, albums, songs, lyrics on AZLyrics',
    'long_description': None,
    'author': 'Adam',
    'author_email': 'adam.wilcz7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
