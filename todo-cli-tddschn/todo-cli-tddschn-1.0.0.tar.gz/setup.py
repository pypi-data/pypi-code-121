# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['todo_cli_tddschn']

package_data = \
{'': ['*']}

install_requires = \
['colorama==0.4.4',
 'fastapi[api]>=0.75.2,<0.76.0',
 'logging-utils-tddschn>=0.1.5,<0.2.0',
 'shellingham==1.4.0',
 'sqlmodel>=0.0.6,<0.0.7',
 'tabulate>=0.8.9,<0.9.0',
 'typer>=0.4.1,<0.5.0',
 'uvicorn[api]>=0.17.6,<0.18.0']

entry_points = \
{'console_scripts': ['todo = todo_cli_tddschn.cli:app']}

setup_kwargs = {
    'name': 'todo-cli-tddschn',
    'version': '1.0.0',
    'description': 'CLI Todo app made with typer, sqlite and a REST API',
    'long_description': "# todo-cli-tddschn\n\nA simple command-line Todo app made with typer, sqlite and a REST API.\n\n- [todo-cli-tddschn](#todo-cli-tddschn)\n\t- [Features](#features)\n\t- [Install](#install)\n\t\t- [pipx (recommended)](#pipx-recommended)\n\t\t- [pip](#pip)\n\t- [Usage](#usage)\n\t\t- [todo](#todo)\n\t\t- [todo ls](#todo-ls)\n\t\t- [todo serve](#todo-serve)\n\t\t- [todo config](#todo-config)\n\t\t- [todo info](#todo-info)\n\t- [Why do you made this?](#why-do-you-made-this)\n\t- [SQLite database schema](#sqlite-database-schema)\n\t- [Screenshots](#screenshots)\n\n## Features\n- Creating, reading, updating, and deleting todos;\n- Nicely formatting the outputs (with color);\n- `todo ls` lists all todos, ordered by priority and due date, the todos without a due date are put last (nullslast).\n- Not only the command line interface - you can also CRUD your todos by making HTTP requests to the [REST API](#todo-serve).\n\n## Install\n\n### pipx (recommended)\n```\npipx install todo-cli-tddschn\n```\n\n### pip\n```\npip install todo-cli-tddschn\n```\n\n## Usage\n\n### todo\n\nYou can add, modify, or remove (all) todos with the `todo` command:\n\n```\ntodo --help\n\nUsage: todo [OPTIONS] COMMAND [ARGS]...\n\n  tddschn's command line todo app\n\nOptions:\n  -v, --version         Show the application's version and exit.\n  --install-completion  Install completion for the current shell.\n  --show-completion     Show completion for the current shell, to copy it or\n                        customize the installation.\n\n  --help                Show this message and exit.\n\nCommands:\n  a        Add a new to-do with a DESCRIPTION.\n  clear    Remove all to-dos.\n  config   Getting and managing the config\n  g        Get a to-do by ID.\n  info     Get infos about todos\n  init     Initialize the to-do database.\n  ls       list all to-dos, ordered by priority and due date.\n  m        Modify a to-do by setting it as done using its TODO_ID.\n  re-init  Re-initialize the to-do database.\n  rm       Remove a to-do using its TODO_ID.\n```\n\n### todo ls\n\nList and filter the todos.\n\n```\ntodo ls --help\n\nUsage: todo ls [OPTIONS] COMMAND [ARGS]...\n\n  list all to-dos, ordered by priority and due date.\n\nOptions:\n  -d, --description TEXT\n  -p, --priority [low|medium|high]\n  -s, --status [todo|done|deleted|cancelled|wip]\n  -pr, --project TEXT\n  -t, --tags TEXT\n  -dd, --due-date [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]\n  --help                          Show this message and exit.\n\nCommands:\n  project  Filter to-dos by project.\n  tag      Filter to-dos by tag.\n```\n\n### todo serve\n\nServe the REST API (built with FastAPI)\n\n```\ntodo serve --help\nUsage: todo serve [OPTIONS]\n\n  serve REST API. Go to /docs for interactive documentation on API usage.\n\nOptions:\n  --host TEXT       [default: 127.0.0.1]\n  --port INTEGER    [default: 5000]\n  --log-level TEXT  [default: info]\n  --help            Show this message and exit.\n```\n\n### todo config\n\nGet or edit the configurations\n\n```\ntodo config --help\n\nUsage: todo config [OPTIONS] COMMAND [ARGS]...\n\n  Getting and managing the config\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  db-path  Get the path to the to-do database.\n  edit     Edit the config file. # Opens in default editor\n  path     Get the path to the config file.\n```\n\n### todo info\n\nGet the info and stats about the todos.\n\n```\ntodo info --help\n\nUsage: todo info [OPTIONS] COMMAND [ARGS]...\n\n  Get infos about todos\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count  Get todo counts\n```\n\n\n## Why do you made this?\n\nFor practicing my python and SQL skills.\n\nIf you're looking for an awesome CLI todo app, try [taskwarrior](https://taskwarrior.org/).\n## SQLite database schema\n\n![schema](images/diagram.png)\n\n## Screenshots\n\n![screenshot](images/screenshot.png)\n\n![screenshot-2](images/screenshot-2.png)\n\n![todo-serve](images/todo-serve.png)\n\n![api-docs](images/api-docs.png)",
    'author': 'Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tddschn/todo-cli-tddschn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
