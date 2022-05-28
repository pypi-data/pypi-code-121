# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['telebot', 'telebot.storages', 'telebot.types']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'pytest-asyncio>=0.18.3,<0.19.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'ujson>=5.3.0,<6.0.0']

setup_kwargs = {
    'name': 'telebot-against-war',
    'version': '0.2.0',
    'description': 'Async-first fork of pyTelegramBotApi',
    'long_description': '<p align="center">\n  <a href="https://pypi.org/project/telebot-against-war/">\n    <img src="https://img.shields.io/pypi/v/telebot-against-war.svg" alt="PyPI package version"/>\n  </a>\n  <a href="https://pypi.org/project/telebot-against-war/">\n    <img src="https://img.shields.io/pypi/pyversions/telebot-against-war.svg" alt="Supported Python versions"/>\n  </a>\n</p>\n\n# <p align="center">telebot\n\n<p align="center">Async-first fork of <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotApi</a>\nlibrary wrapping the <a href="https://core.telegram.org/bots/api">Telegram Bot API</a>.</p>\n\n<p align="center">Supported Bot API version: <a href="https://core.telegram.org/bots/api#april-16-2022">6.0</a>!\n\n<h2 align="center">See upstream project <a href=\'https://pytba.readthedocs.io/en/latest/index.html\'>docs</a> and \n<a href=\'https://github.com/eternnoir/pyTelegramBotAPI/blob/master/README.md\'>README</a></h2>\n\n\n## Usage\n\nTBD: what is different from upstream pyTelegramBotApi?\n\n\n## Development\n\nThe project uses [Poetry](https://python-poetry.org/) to manage dependencies, build and publish the package.\nInstall as described [here](https://python-poetry.org/docs/master/#installation) and make sure to update\nto the latest `1.2.x` version:\n\n```bash\npoetry self update 1.2.0b1\n```\n\n\n### Installing and configuring locally\n\n```bash\npoetry install\npoetry run pre-commit install\n```\n\n### Running tests and linters\n\n```bash\npoetry shell\n\npytest tests -vv\n\nmypy telebot\n\nblack .\nisort .\n```\n\n### Building\n\n```bash\npoetry plugin add poetry-dynamic-versioning\npoetry build\npoetry publish -u <pypi-username> -p <pypi-pwd>\n```\n',
    'author': 'Igor Vaiman',
    'author_email': 'gosha.vaiman@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/bots-against-war/telebot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
