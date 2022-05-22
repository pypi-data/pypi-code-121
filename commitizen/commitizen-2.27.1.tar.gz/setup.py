# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['commitizen',
 'commitizen.commands',
 'commitizen.config',
 'commitizen.cz',
 'commitizen.cz.conventional_commits',
 'commitizen.cz.customize',
 'commitizen.cz.jira']

package_data = \
{'': ['*'], 'commitizen': ['templates/*']}

install_requires = \
['argcomplete>=1.12.1,<2.0.0',
 'colorama>=0.4.1,<0.5.0',
 'decli>=0.5.2,<0.6.0',
 'jinja2>=2.10.3',
 'packaging>=19,<22',
 'pyyaml>=3.08',
 'questionary>=1.4.0,<2.0.0',
 'termcolor>=1.1,<2.0',
 'tomlkit>=0.5.3,<1.0.0',
 'typing-extensions>=4.0.1,<5.0.0']

entry_points = \
{'console_scripts': ['cz = commitizen.cli:main',
                     'git-cz = commitizen.cli:main']}

setup_kwargs = {
    'name': 'commitizen',
    'version': '2.27.1',
    'description': 'Python commitizen client tool',
    'long_description': '[![Github Actions](https://github.com/commitizen-tools/commitizen/workflows/Python%20package/badge.svg?style=flat-square)](https://github.com/commitizen-tools/commitizen/actions)\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)\n[![PyPI Package latest release](https://img.shields.io/pypi/v/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)\n[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/commitizen?style=flat-square)](https://pypi.org/project/commitizen/)\n[![Supported versions](https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)\n[![homebrew](https://img.shields.io/homebrew/v/commitizen?color=teal&style=flat-square)](https://formulae.brew.sh/formula/commitizen)\n[![Codecov](https://img.shields.io/codecov/c/github/commitizen-tools/commitizen.svg?style=flat-square)](https://codecov.io/gh/commitizen-tools/commitizen)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n![Using commitizen cli](images/demo.gif)\n\n---\n\n**Documentation:** [https://commitizen-tools.github.io/commitizen/](https://commitizen-tools.github.io/commitizen/)\n\n---\n\n## About\n\nCommitizen is a tool designed for teams.\n\nIts main purpose is to define a standard way of committing rules\nand communicating it (using the cli provided by commitizen).\n\nThe reasoning behind it is that it is easier to read, and enforces writing\ndescriptive commits.\n\nBesides that, having a convention on your commits makes it possible to\nparse them and use them for something else, like generating automatically\nthe version or a changelog.\n\n### Commitizen features\n\n- Command-line utility to create commits with your rules. Defaults: [Conventional commits][conventional_commits]\n- Display information about your commit rules (commands: schema, example, info)\n- Bump version automatically using [semantic versioning][semver] based on the commits. [Read More](./bump.md)\n- Generate a changelog using [Keep a changelog][keepchangelog]\n\n## Requirements\n\nPython 3.6+\n\n[Git][gitscm] `1.8.5.2`+\n\n## Installation\n\nGlobal installation\n\n```bash\nsudo pip3 install -U Commitizen\n```\n\n### Python project\n\nYou can add it to your local project using one of these:\n\n```bash\npip install -U commitizen\n```\n\n```bash\npoetry add commitizen --dev\n```\n\n### macOS\n\nOn macOS, it can also be installed via [homebrew](https://formulae.brew.sh/formula/commitizen):\n\n```bash\nbrew install commitizen\n```\n\n## Usage\n\n### Committing\n\nRun in your terminal\n\n```bash\ncz commit\n```\n\nor the shortcut\n\n```bash\ncz c\n```\n\n#### Sign off the commit\n\nRun in the terminal\n\n```bash\ncz commit --signoff\n```\n\nor the shortcut\n\n```bash\ncz commit -s\n```\n\n### Integrating with Pre-commit\nCommitizen can lint your commit message for you with `cz check`.\nYou can integrate this in your [pre-commit](https://pre-commit.com/) config with:\n\n```yaml\n---\nrepos:\n  - repo: https://github.com/commitizen-tools/commitizen\n    rev: master\n    hooks:\n      - id: commitizen\n```\n\nAfter the configuration is added, you\'ll need to run\n\n```sh\npre-commit install --hook-type commit-msg\n```\n\nRead more about the `check` command [here](check.md).\n\n### Help\n\n```sh\n$ cz --help\nusage: cz [-h] [--debug] [-n NAME] [-nr NO_RAISE] {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version} ...\n\nCommitizen is a cli tool to generate conventional commits.\nFor more information about the topic go to https://conventionalcommits.org/\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --debug               use debug mode\n  -n NAME, --name NAME  use the given commitizen (default: cz_conventional_commits)\n  -nr NO_RAISE, --no-raise NO_RAISE\n                        comma separated error codes that won\'t rise error, e.g: cz -nr 1,2,3 bump. See codes at https://commitizen-\n                        tools.github.io/commitizen/exit_codes/\n\ncommands:\n  {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version}\n    init                init commitizen configuration\n    commit (c)          create new commit\n    ls                  show available commitizens\n    example             show commit example\n    info                show information about the cz\n    schema              show commit schema\n    bump                bump semantic version based on the git log\n    changelog (ch)      generate changelog (note that it will overwrite existing file)\n    check               validates that a commit message matches the commitizen schema\n    version             get the version of the installed commitizen or the current project (default: installed commitizen)\n```\n\n## Setting up bash completion\n\nWhen using bash as your shell (limited support for zsh, fish, and tcsh is available), Commitizen can use [argcomplete](https://kislyuk.github.io/argcomplete/) for auto-completion. For this argcomplete needs to be enabled.\n\nargcomplete is installed when you install Commitizen since it\'s a dependency.\n\nIf Commitizen is installed globally, global activation can be executed:\n\n```bash\nsudo activate-global-python-argcomplete\n```\n\nFor permanent (but not global) Commitizen activation, use:\n\n```bash\nregister-python-argcomplete cz >> ~/.bashrc\n```\n\nFor one-time activation of argcomplete for Commitizen only, use:\n\n```bash\neval "$(register-python-argcomplete cz)"\n```\n\nFor further information on activation, please visit the [argcomplete website](https://kislyuk.github.io/argcomplete/).\n\n[conventional_commits]: https://www.conventionalcommits.org\n[semver]: https://semver.org/\n[keepchangelog]: https://keepachangelog.com/\n[gitscm]: https://git-scm.com/downloads\n',
    'author': 'Santiago Fraire',
    'author_email': 'santiwilly@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/commitizen-tools/commitizen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
