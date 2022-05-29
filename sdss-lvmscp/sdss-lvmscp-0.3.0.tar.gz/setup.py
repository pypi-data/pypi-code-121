# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['lvmscp', 'lvmscp.actor', 'lvmscp.actor.commands']

package_data = \
{'': ['*'], 'lvmscp': ['etc/*']}

install_requires = \
['Authlib>=1.0.0rc1',
 'click-default-group>=1.2.2,<2.0.0',
 'click>=8.1.2,<9.0.0',
 'httpx>=0.18.1',
 'sdss-archon>=0.6.0,<0.7.0',
 'sdss-clu>=1.6.1,<2.0.0',
 'sdsstools>=0.4.0']

entry_points = \
{'console_scripts': ['lvmscp = lvmscp.__main__:lvmscp']}

setup_kwargs = {
    'name': 'sdss-lvmscp',
    'version': '0.3.0',
    'description': 'LVM spectrograph control package.',
    'long_description': '# lvmscp\n\n![Versions](https://img.shields.io/badge/python->3.8-blue)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Documentation Status](https://readthedocs.org/projects/lvmscp/badge/?version=latest)](https://lvmscp.readthedocs.io/en/latest/?badge=latest)\n[![Test](https://github.com/sdss/lvmscp/actions/workflows/test.yml/badge.svg)](https://github.com/sdss/lvmscp/actions/workflows/test.yml)\n[![Docker](https://github.com/sdss/lvmscp/actions/workflows/docker.yml/badge.svg)](https://github.com/sdss/lvmscp/actions/workflows/docker.yml)\n[![codecov](https://codecov.io/gh/sdss/lvmscp/branch/main/graph/badge.svg?token=RYKAKyfNpZ)](https://codecov.io/gh/sdss/lvmscp)\n\nSDSS-V LVM (Local Volume Mapper) control software for the spectrograph system.\n\n## Quick Start\n\n### Installation\n\n`lvmscp` uses the [CLU](https://clu.readthedocs.io/en/latest/) framework and requires a RabbitMQ instance running in the background.\n\n`lvmscp` can be installed using `pip`\n\n```console\npip install sdss-lvmscp\n```\n\nor by cloning this repository\n\n```console\ngit clone https://github.com/sdss/lvmscp\n```\n\nThe preferred installation for development is using [poetry](https://python-poetry.org/)\n\n```console\ncd lvmscp\npoetry install\n```\n\n\n### Basic ping-pong test\n\nStart the `lvmscp` actor.\n\n```console\nlvmscp start\n```\n\nIn another terminal, type `clu` and `lvmscp ping` for test.\n\n```console\n$ clu\nlvmscp ping\n07:41:22.636 lvmscp >\n07:41:22.645 lvmscp : {\n    "text": "Pong."\n}\n```\n\nStop `lvmscp` actor.\n\n```console\nlvmscp stop\n```\n',
    'author': 'Changgon Kim',
    'author_email': 'changgonkim@khu.ac.kr',
    'maintainer': 'José Sánchez-Gallego',
    'maintainer_email': 'gallegoj@uw.edu',
    'url': 'https://github.com/sdss/lvmscp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
