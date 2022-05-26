# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clitify']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.4.4,<13.0.0', 'spotipy>=2.19.0,<3.0.0', 'termcolors>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'clitify',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Marc Partensky',
    'author_email': 'marc.partensky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
