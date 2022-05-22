# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asset_downloader']

package_data = \
{'': ['*']}

install_requires = \
['python-slugify', 'pytube', 'requests', 'typer']

entry_points = \
{'console_scripts': ['adw = asset_downloader.__main__:app']}

setup_kwargs = {
    'name': 'asset-downloader',
    'version': '0.1.4',
    'description': 'My editing pal',
    'long_description': None,
    'author': 'Antonio Feregrino',
    'author_email': 'antonio.feregrino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
