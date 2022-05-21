# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['PyDrocsid', 'PyDrocsid.database']

package_data = \
{'': ['*'], 'PyDrocsid': ['translations/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'SQLAlchemy>=1.4.32,<2.0.0',
 'aenum>=3.1.8,<4.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'aiomysql>=0.1.0,<0.2.0',
 'aioredis>=2.0.1,<3.0.0',
 'asyncpg>=0.25.0,<0.26.0',
 'httpx>=0.22.0,<0.23.0',
 'py-cord>=2.0.0b7,<3.0.0',
 'sentry-sdk>=1.5.8,<2.0.0']

setup_kwargs = {
    'name': 'pydrocsid',
    'version': '2.3.2',
    'description': 'Python Discord Bot Framework based on pycord',
    'long_description': '<!-- markdownlint-disable-next-line MD033 -->\n<p>\n\n  <!-- markdownlint-disable-next-line MD041 -->\n  [![CI](https://github.com/PyDrocsid/library/actions/workflows/ci.yml/badge.svg)](https://github.com/PyDrocsid/library/actions/workflows/ci.yml)\n  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n  [![Maintainability](https://api.codeclimate.com/v1/badges/cf9f606da13c20077022/maintainability)](https://codeclimate.com/github/PyDrocsid/library/maintainability)\n  [![PyPI](https://img.shields.io/pypi/v/PyDrocsid.svg)](https://pypi.org/project/PyDrocsid/)\n  [![PyPI Downloads](https://img.shields.io/pypi/dm/PyDrocsid.svg)](https://pypi.org/project/PyDrocsid/)\n  [![Discord](https://img.shields.io/discord/637234990404599809.svg?label=Discord&logo=discord&logoColor=ffffff&color=7389D8)](https://pydrocsid.defelo.de/discord)\n  [![Matrix](https://img.shields.io/matrix/pydrocsid:matrix.defelo.de.svg?label=Matrix&logo=matrix&logoColor=ffffff&color=4db798)](https://pydrocsid.defelo.de/matrix)\n\n</p>\n\n\n# PyDrocsid\n\nPython Discord Bot Framework based on [Pycord](https://pycord.dev/)\n',
    'author': 'Defelo',
    'author_email': 'elodef42@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PyDrocsid/library',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
