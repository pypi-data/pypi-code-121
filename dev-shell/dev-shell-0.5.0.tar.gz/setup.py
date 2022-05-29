# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dev_shell', 'dev_shell.command_sets', 'dev_shell.tests', 'dev_shell.utils']

package_data = \
{'': ['*']}

install_requires = \
['cmd2']

extras_require = \
{':sys_platform == "darwin"': ['gnureadline']}

entry_points = \
{'console_scripts': ['devshell = dev_shell.dev_shell_app:devshell_cmdloop']}

setup_kwargs = {
    'name': 'dev-shell',
    'version': '0.5.0',
    'description': 'Devloper shell for easy startup...',
    'long_description': '# A "dev-shell" for Python projects ;)\n\n[![pytest](https://github.com/jedie/dev-shell/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/jedie/dev-shell/actions?query=branch%3Amain)\n[![codecov](https://codecov.io/gh/jedie/dev-shell/branch/main/graph/badge.svg)](https://codecov.io/gh/jedie/dev-shell)\n\nThis small project is intended to improve the start-up for collaborators.\n\nThe idea is to make the project setup as simple as possible. Just clone the sources and start a script and you\'re done ;)\n\nRun Tests? Just start the script and call the "run test command".\n\nThe "dev-shell" is the base to create a CLI and a shell. It also\n\nIt also shows how to make a project bootstrap as simply as possible, e.g.:\n\n```bash\n~$ git clone https://github.com/jedie/dev-shell.git\n~$ cd dev-shell\n~/dev-shell$ ./devshell.py pytest\n```\n\n\n## How it works\n\nFirst start of the Python script [./devshell.py](https://github.com/jedie/dev-shell/blob/main/devshell.py) will bootstrap:\n\n* Generate a Python virtual environment (in short: `venv`)\n* Install poetry\n* Install project dependencies and the project himself\n\nThe output on first bootstrap start looks like:\n\n```bash\n~/dev-shell$ ./devshell.py\nCreate venv here: ~/dev-shell/.venv\nCollecting pip\n...\nSuccessfully installed pip-21.0.1\nCollecting poetry\n...\nInstalling dependencies from lock file\n\nPackage operations: 31 installs, 1 update, 0 removals\n\n...\n\nInstalling the current project: dev-shell (0.0.1alpha0)\n\n\n+ .venv/bin/python .venv/bin/devshell\n\n\nDeveloper shell - dev_shell - v0.2.0\n\n\nDocumented commands (use \'help -v\' for verbose/\'help <topic>\' for details):\n\ndev-shell commands\n==================\nfix_code_style  linting  list_venv_packages  publish  pytest  update\n\n...\n\n(dev_shell) quit\n~/dev-shell$\n```\n\nThe first bootstrap start takes a few seconds. Each later startup detects the existing virtualenv and is very fast:\n\n```bash\n~/dev-shell$ ./devshell.py\n\nDeveloper shell - dev_shell - v0.2.0\n\n(dev_shell) help\n```\n\nInfo: The `.venv` will be automatically updated via `poetry install` call if the `poetry.lock` file has been changed.\n\nA call with `--update` will force to call some create/update steps, e.g.:\n\n```bash\n~/dev-shell$ ./devshell.py --update\n```\n\nYou can also just delete `/.venv/` and start `devshell.py` again ;)\n\n(Using `--update` is not to be confused with the call of "update" command.)\n\n\n## compatibility\n\n| dev-shell version | OS                      | Python version |\n|-------------------|-------------------------|----------------|\n| >=v0.0.1          | Linux + MacOS + Windows | 3.9, 3.8, 3.7  |\n\nSee also github test configuration: [.github/workflows/test.yml](https://github.com/jedie/dev-shell/blob/main/.github/workflows/test.yml)\n\n## History\n\n* [*dev*](https://github.com/jedie/dev-shell/compare/v0.5.0...main)\n  * TBC\n* [0.5.0.rc1 - 2022-05-29](https://github.com/jedie/dev-shell/compare/v0.4.0...v0.5.0)\n  * Add "tox" and "poetry" commands to call them installed in created {{{.venv}}} \n  * Update requirements\n* [v0.4.0 - 2022-02-28](https://github.com/jedie/dev-shell/compare/v0.3.0...v0.4.0)\n  * Update to new cmd2, colorama and pytest versions\n* [v0.3.0 - 2022-01-30](https://github.com/jedie/dev-shell/compare/v0.2.4...v0.3.0)\n  * Remove "flynt" form linting/fix code style\n* [v0.2.4 - 2022-01-30](https://github.com/jedie/dev-shell/compare/v0.2.3...v0.2.4)\n  * Update requirements\n  * Use darker as code formatter and pytest-darker for linting\n* [v0.2.3 - 2021-11-15](https://github.com/jedie/dev-shell/compare/v0.2.2...v0.2.3)\n  * Update requirements\n  * [Flynt arguments can be changes via CommandSet](https://github.com/jedie/dev-shell/issues/29)\n* [v0.2.2 - 2021-04-13](https://github.com/jedie/dev-shell/compare/v0.2.1...v0.2.2)\n  * Include bootstrap file, to it\'s possible to use it in external projects, too.\n* [v0.2.1 - 2021-04-12](https://github.com/jedie/dev-shell/compare/v0.2.0...v0.2.1)\n  * Handle if "poetry-publish" is not installed, so a project that used "dev-shell" must not install it.\n* [v0.2.0 - 2021-04-11](https://github.com/jedie/dev-shell/compare/v0.1.0...v0.2.0)\n  * Rename: "dev-shell.py => devshell.py" because of better autocomplete\n  * Add `DevShellConfig.base_path` and use it in own commands like, `pytest`, `linting` etc. (So they are usable in external project, too.)\n  * recognize "--update" and "--help" arguments better in `./devshell.py` calls.\n  * Update `setuptools` on `.venv` creation, too.\n  * Fix Bugs/tests under Windows\n* [v0.1.0 - 2021-03-22](https://github.com/jedie/dev-shell/compare/v0.0.2...v0.1.0)\n  * Fix CI usage: Exit with correct return code if tests failed\n  * Better "run as CLI" implementation via new `run_cmd2_app()`\n  * Bugfix errors that only occur on Windows.\n  * Simplify `devshell.py` boot script and fix raise error if `ensurepip` missing\n* [v0.0.2 - 2021-03-19](https://github.com/jedie/dev-shell/compare/v0.0.1...v0.0.2)\n  * refactor colorful shortcuts\n  * display subprocess calls with separated colors\n* [v0.0.1 - 2021-03-19](https://github.com/jedie/dev-shell/compare/ad5dca...v0.0.1)\n  * first "useable" version\n\n## Project links\n\n* Github: https://github.com/jedie/dev-shell/\n* PyPi: https://pypi.org/project/dev-shell/\n',
    'author': 'Jens Diemer',
    'author_email': 'python@jensdiemer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jedie/dev-shell',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
