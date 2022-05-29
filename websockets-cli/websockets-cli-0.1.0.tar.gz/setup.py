# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ws', 'ws.commands', 'ws.utils']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.5.0,<4.0.0',
 'certifi>=2021.10.8,<2022.0.0',
 'click-didyoumean>=0.3.0,<0.4.0',
 'click>=8.0.4,<9.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'rich>=12.0.0,<13.0.0',
 'shellingham>=1.4.0,<2.0.0',
 'tomli>=2.0.1,<3.0.0',
 'trio-websocket>=0.9.2,<0.10.0']

entry_points = \
{'console_scripts': ['ws = ws.main:cli']}

setup_kwargs = {
    'name': 'websockets-cli',
    'version': '0.1.0',
    'description': 'A simple yet powerful websocket cli',
    'long_description': '# ws\n\n[![Pypi version](https://img.shields.io/pypi/v/ws.svg)](https://pypi.org/project/ws/)\n![](https://github.com/lewoudar/ws/workflows/CI/badge.svg)\n[![Coverage Status](https://codecov.io/gh/lewoudar/ws/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/gh/lewoudar/ws)\n[![Documentation Status](https://readthedocs.org/projects/pyws/badge/?version=latest)](https://pyws.readthedocs.io/en/latest/?badge=latest)\n[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/wntrblm/nox)\n[![License Apache 2](https://img.shields.io/hexpm/l/plug.svg)](http://www.apache.org/licenses/LICENSE-2.0)\n\nA simple yet powerful websocket cli.\n\n## Why?\n\nEach time I work on a web project involving websockets, I found myself wanting a simple (cli) tool to test what I have\ncoded. What I often do is to write a python script using [websockets](https://websockets.readthedocs.io/en/stable/).\nThere are graphical tools like [Postman](https://www.postman.com/), but I\'m not confortable with.\nSo I decided to write a cli tool for this purpose.\n\n## Installation\n\nYou can install the cli with `pip`:\n\n```shell\n$ pip install ws\n```\n\nor use a better package manager like [poetry](https://python-poetry.org/docs/):\n\n```shell\n# you probably want to add this dependency as a dev one, this is why I put -D into square brackets\n$ poetry add [-D] ws\n```\n\nws starts working from **python3.7** and also supports **pypy3**. It has the following dependencies:\n\n- [trio](https://trio.readthedocs.io/en/stable/) / [anyio](https://anyio.readthedocs.io/en/stable/) for structured\n  (async) concurrency support.\n- [trio-websocket](https://trio-websocket.readthedocs.io/en/stable/) the library implementing the websocket protocol.\n- [pydantic](https://pydantic-docs.helpmanual.io/) / [python-dotenv](https://pypi.org/project/python-dotenv/) for\n  input validation and settings management.\n- [certifi](https://pypi.org/project/certifi/) to manage TLS and certificates.\n- [click](https://click.palletsprojects.com/en/8.1.x/) to write the cli.\n- [click-didyoumean](https://pypi.org/project/click-didyoumean/) for command suggestions in case of typos.\n- [rich](https://rich.readthedocs.io/en/latest/) for beautiful output display.\n- [shellingham](https://pypi.org/project/shellingham/) to detect the shell used.\n\n## Usage\n\nThe usage is straightforward and the cli is well documented.\n\n```shell\n$ ws\nUsage: ws [OPTIONS] COMMAND [ARGS]...\n\n  A convenient websocket cli.\n\nOptions:\n  --version   Show the version and exit.\n  -h, --help  Show this message and exit.\n\nCommands:\n  byte                Sends binary message to URL endpoint.\n  echo-server         Runs an echo websocket server.\n  install-completion  Install completion script for bash, zsh and fish...\n  listen              Listens messages on a given URL.\n  ping                Pings a websocket server located at URL.\n  pong                Sends a pong to websocket server located at URL.\n  session             Opens an interactive session to communicate with...\n  tail                An emulator of the tail unix command that output...\n  text                Sends text message on URL endpoint.\n\n```\n\nThe first command to use is `install-completion` to have auto-completion for commands and options using the `TAB` key.\nAuto-completion is available on `bash`, `fish` and `zsh`. For Windows users, I don\'t forget you (I\'m also a Windows\nuser), support is planned for `Powershell` ;)\n\n```shell\n$ ws install-completion\n# when the command succeeded, you should see the following message\nSuccessfully installed completion script!\n```\n\nTo play with the api you can use the websocket server kindly provided by the\n[Postman](https://blog.postman.com/introducing-postman-websocket-echo-service/) team at wss://ws.postman-echo.com/raw or\nspawn a new one with the following command:\n\n```shell\n# it will listen incoming messages on port 8000, to stop it, just type Ctrl+C\n$ ws echo-server -p 8000\nRunning server on localhost:8000 💫\n```\n\nTo *ping* the server, you can do this:\n\n```shell\n# :8000 is a\n$ ws ping :8000\nPING ws://localhost:8000 with 32 bytes of data\nsequence=1, time=0.00s\n```\n\nTo send a message, you can type this:\n\n```shell\n# Sends a text frame\n$ ws text :8000 "hello world"  # on Windows it is probably better to use single quotes \'hello world\'\nSent 11.0 B of data over the wire.\n\n# Sends a binary frame\n$ ws byte :8000 "hello world"\nSent 11.0 B of data over the wire.\n```\n\nIf you know that you will have a long interaction with the server, it is probably better to use the `session` subcommand.\n\n```shell\n$ ws session wss://ws.postman-echo.com/raw\nWelcome to the interactive websocket session! 🌟\nFor more information about commands, type the help command.\nWhen you see <> around a word, it means this argument is optional.\nTo know more about a particular command type help <command>.\nTo close the session, you can type Ctrl+D or the quit command.\n\n> ping "with payload"\nPING wss://ws.postman-echo.com/raw with 12 bytes of data\nTook 0.16s to receive a PONG.\n\n> quit\nBye! 👋\n```\n## Documentation\n\nThe full documentation can be found at https://pyws.readthedocs.io\n\n## Limitations\n\nThe cli does not support [RFC 7692](https://datatracker.ietf.org/doc/html/rfc7692) and\n[RFC 8441](https://datatracker.ietf.org/doc/html/rfc8441) because `trio_websocket` the underlying library used for\nwebsockets does not support it.\n',
    'author': 'le_woudar',
    'author_email': 'lewoudar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pyws.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
