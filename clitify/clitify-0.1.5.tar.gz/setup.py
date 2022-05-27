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
    'version': '0.1.5',
    'description': 'CLI for the Spotify API using Spotipy',
    'long_description': '![https://pypi.org/project/clitify/](https://cdn.discordapp.com/attachments/507519157387132940/979538526259523615/unknown.png)\n\n# Install\n```sh\npip install clitify\n```\n\n# Run\n```sh\n# Like a song\nsplike\n\n# Move song position\nspseek +10 # +10 seconds\nspseek -2.5 # -2.5 seconds\n\n# List song queue when on playlist\nspq\n```\n\n# Source\n[![github.com/marcpartensky/clitify](https://cdn-icons-png.flaticon.com/512/25/25231.png)](https://github.com/marcpartensky/clitify))\n',
    'author': 'Marc Partensky',
    'author_email': 'marc.partensky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marcpartensky/clitify',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
