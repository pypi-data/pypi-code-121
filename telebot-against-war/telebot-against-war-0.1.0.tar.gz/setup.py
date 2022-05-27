# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['telebot', 'telebot.asyncio_storage', 'telebot.storage']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'telebot-against-war',
    'version': '0.1.0',
    'description': 'Async-first fork of pyTelegramBotApi',
    'long_description': '\n<!-- [![PyPi Package Version](https://img.shields.io/pypi/v/pyTelegramBotAPI.svg)](https://pypi.python.org/pypi/pyTelegramBotAPI)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyTelegramBotAPI.svg)](https://pypi.python.org/pypi/pyTelegramBotAPI)\n[![PyPi status](https://img.shields.io/pypi/status/pytelegrambotapi.svg?style=flat-square)](https://pypi.python.org/pypi/pytelegrambotapi) -->\n\n# <p align="center">telebot\n\n<p align="center">Async-first fork of <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotApi</a>\nlibrary wrapping the <a href="https://core.telegram.org/bots/api">Telegram Bot API</a>.</p>\n\n<p align="center">Supported Bot API version: <a href="https://core.telegram.org/bots/api#april-16-2022">6.0</a>!\n\n<h2 align="center">See upstream project <a href=\'https://pytba.readthedocs.io/en/latest/index.html\'>docs</a> and \n<a href=\'https://github.com/eternnoir/pyTelegramBotAPI/blob/master/README.md\'>README</a></h2>\n\n\n## Usage\n\nTBD: what is different from upstream pyTelegramBotApi?\n\n\n## Development\n\nThe project uses [Poetry](https://python-poetry.org/) to track dependencies and build package.\nInstall as described [here](https://python-poetry.org/docs/#installation).\n\n\n',
    'author': 'Igor Vaiman',
    'author_email': 'gosha.vaiman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bots-against-war/telebot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
