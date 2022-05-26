# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_pp']

package_data = \
{'': ['*']}

install_requires = \
['utils-tddschn==0.1.6', 'uvloop[uvloop]>=0.16.0,<0.17.0']

entry_points = \
{'console_scripts': ['git-pp = git_pp.git_pp:main_sync']}

setup_kwargs = {
    'name': 'git-pp',
    'version': '1.10.5',
    'description': 'A (tiny) Git utility for auto-committing and concurrent pushing',
    'long_description': '# git pp\n\nA (tiny) Git utility for auto-committing and concurrent pushing.\n\nPowered by `asyncio`, with no dependency besides `python>=3.10` and `git`.\n\n- [git pp](#git-pp)\n  - [Features](#features)\n  - [Demo](#demo)\n  - [Use cases and example usage](#use-cases-and-example-usage)\n  - [Installation](#installation)\n    - [pipx](#pipx)\n    - [pip](#pip)\n    - [AUR](#aur)\n  - [Usage](#usage)\n  - [Develop](#develop)\n## Features\n- Auto-stages and commits with custom or generated commit messages\n- Pushes to multiple or all remotes of a git repository **concurrently** with `asyncio`\n- Operates on **any number of git repositories** at the same time\n\n## Demo\n\n<!-- [![asciicast](https://asciinema.org/a/487579.png)](https://asciinema.org/a/487579) -->\n<!-- <a href="https://asciinema.org/a/487579"><img src="https://asciinema.org/a/487579.png" alt="asciicast" style="width:500px;height:300px;"></a> -->\n<a href="https://asciinema.org/a/487579"><img src="https://asciinema.org/a/487579.svg" alt="Asciicast" width="650"/></a>\n\nIn this demo, git pp did the following in \\~/config and \\~/gui repos:\n\n- (Concurrently) Auto staged all changes and commits with ISO-8601 timestamps as commit messages;\n- (Concurrently) Pushed the changes in the checked out branch to all of their remotes, in this case, they’re origin and lab.\n\n## Use cases and example usage\n- You have multiple remotes registered on a local git repository (or more)\nand want to push the changes to all or some of the remotes fast and efficiently.\n\n```bash\n# Use --push-only or -po\n\n$ git pp --push-only # this pushes to all remotes of the current git repository, does not stages or commits\n$ git pp --push-only --remote [one or more remotes] # only pushes to the specified remotes\n$ git pp -po --timeout 10 # terminates pushing to one remotes if it takes more than 10 seconds\n$ git pp -po -b dev ~/my-proj ~/my-proj2 # pushes the dev branch to all remotes in ~/my-proj and ~/my-proj2 repository\n```\n\n- You\'re tired of using `git add --all && git commit` every time you make a little change\nand want to automate this across one or more repositories.\n\n```bash\n$ git pp # stages all files in the current git repository and commits with a timestamp as the commit message\n$ git pp -m \'Initial commit\' # custom commit message\n$ git pp --no-status # don\'t show git status and git add outputs\n```\n\nAnd you can do both of the above (auto-commit and push) with `--push`:\n```bash\n# Use --push or -p\n\n$ git pp --push # stages, commits and pushes to all remotes.\n$ git pp --push --remote [one or more remotes]\n$ git pp -p --timeout 10\n$ git pp -p -b dev ~/my-proj ~/my-proj2\n```\n\n## Installation\n\nFirst make sure the `git` executable is installed and in your `$PATH`.\n\nNote that non-UNIX systems are not officially supported.\n\n### pipx\n\nThis is the recommended installation method.\n\n```\n$ pipx install git-pp\n```\n\n### [pip](https://pypi.org/project/git-pp/)\n```\n$ pip install git-pp\n```\n\n### [AUR](https://aur.archlinux.org/packages/python-git-pp)\nFor Archlinux.\n```\n$ yay -S python-git-pp\n```\n\n\n## Usage\n\nYou can either invoke this tool with `git-pp` or `git pp`,\n`--help` is unsupported when using the latter.\n\n```\n$ git pp -h\nusage: git pp [-h] [-m COMMIT_MESSAGE] [-v] [-so] [-p] [-po] [-r REMOTE [REMOTE ...]] [-b BRANCH] [-f] [-t TIMEOUT] [DIRS ...]\n\nGit utility for auto-committing and concurrent pushing\n\npositional arguments:\n  DIRS                  Dirs to operate on (default: [\'.\'])\n\noptions:\n  -h, --help            show this help message and exit\n  -m COMMIT_MESSAGE, --commit-message COMMIT_MESSAGE\n                        commit message (default: None)\n  -v, --version         show program\'s version number and exit\n  -so, --status-only    Prints status only (default: False)\n  -p, --push            Push to all remotes (default: False)\n  -po, --push-only      Push to all remotes, without pre_pull (default: False)\n  -r REMOTE [REMOTE ...], --remote REMOTE [REMOTE ...]\n                        Remote name (default: None)\n  -b BRANCH, --branch BRANCH\n                        Branch name (default: None)\n  -f, --force           Force push (default: False)\n  -t TIMEOUT, --timeout TIMEOUT\n                        Timeout for a single push (default: None)\n```\n\n## Develop\n```\n$ git clone https://github.com/tddschn/git-pp.git\n$ cd git-pp\n$ poetry install\n```',
    'author': 'Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tddschn/git-pp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
