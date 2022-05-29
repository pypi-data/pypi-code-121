# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['lvmieb', 'lvmieb.actor', 'lvmieb.actor.commands', 'lvmieb.controller']

package_data = \
{'': ['*'], 'lvmieb': ['etc/*']}

install_requires = \
['click-default-group>=1.2.2,<2.0.0',
 'numpy>=1.20.3,<2.0.0',
 'sdss-clu>=1.6.1,<2.0.0',
 'sdss-drift>=0.4.2,<0.5.0',
 'sdsstools>=0.4.0']

entry_points = \
{'console_scripts': ['lvmieb = lvmieb.__main__:lvmieb']}

setup_kwargs = {
    'name': 'sdss-lvmieb',
    'version': '0.4.0',
    'description': 'Control software for the Local Volume Mapper Instrument Electronics Box',
    'long_description': '# lvmieb\n\n![Versions](https://img.shields.io/badge/python->3.8-blue)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Documentation Status](https://readthedocs.org/projects/lvmieb/badge/?version=latest)](https://lvmieb.readthedocs.io/en/latest/?badge=latest)\n[![Test](https://github.com/sdss/lvmieb/actions/workflows/test.yml/badge.svg)](https://github.com/sdss/lvmieb/actions/workflows/test.yml)\n[![Docker](https://github.com/sdss/lvmieb/actions/workflows/docker.yml/badge.svg)](https://github.com/sdss/lvmieb/actions/workflows/docker.yml)\n[![codecov](https://codecov.io/gh/sdss/lvmieb/branch/main/graph/badge.svg?token=IyQglaQYSF)](https://codecov.io/gh/sdss/lvmieb)\n\nControl software for the SDSS-V LVM (Local Volume Mapper) spectrograph Instrument Electronics Box (IEB).\n\n## Quick Start\n\n### Installation\n\n`lvmieb` uses the [CLU](https://clu.readthedocs.io/en/latest/) framework and requires a RabbitMQ instance running in the background.\n\n`lvmieb` can be installed using `pip`\n\n```console\npip install sdss-lvmieb\n```\n\nor by cloning this repository\n\n```console\ngit clone https://github.com/sdss/lvmieb\n```\n\nThe preferred installation for development is using [poetry](https://python-poetry.org/)\n\n```console\ncd lvmieb\npoetry install\n```\n\n\n### Basic ping-pong test\n\nStart the `lvmieb` actor.\n\n```console\nlvmieb start\n```\n\nIn another terminal, type `clu` and `lvmieb ping` for test.\n\n```console\n$ clu\nlvmieb ping\n07:41:22.636 lvmieb >\n07:41:22.645 lvmieb : {\n    "text": "Pong."\n}\n```\n\nStop `lvmieb` actor.\n\n```console\nlvmieb stop\n```\n',
    'author': 'Changgon Kim',
    'author_email': 'changgonkim@khu.ac.kr',
    'maintainer': 'José Sánchez-Gallego',
    'maintainer_email': 'gallegoj@uw.edu',
    'url': 'https://github.com/sdss/lvmieb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
