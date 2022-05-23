# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitignore_cli_tddschn']

package_data = \
{'': ['*']}

install_requires = \
['utils-tddschn>=1.0.0']

entry_points = \
{'console_scripts': ['gi = gitignore_cli_tddschn.cli:main',
                     'gitignore = gitignore_cli_tddschn.cli:main']}

setup_kwargs = {
    'name': 'gitignore-cli-tddschn',
    'version': '0.4.0',
    'description': 'Fast gitignore CLI tool with cached templates',
    'long_description': "# gitignore CLI\n\nFast gitignore CLI tool with cached templates\n\n[Templates source](https://github.com/toptal/gitignore)\n\n- [gitignore CLI](#gitignore-cli)\n\t- [Features](#features)\n\t- [Installation](#installation)\n\t\t- [pipx](#pipx)\n\t\t- [pip](#pip)\n\t- [Usage](#usage)\n\t- [Develop](#develop)\n## Features\n- Extremely fast - no network calls made if the cache has been retrieved with `gi --refresh`.\n\n## Installation\n\nFirst make sure the `git` executable is installed and in your `$PATH`, \nas it is required to retrieve the gitignore templates.\n\n### pipx\n\nThis is the recommended installation method.\n\n```\n$ pipx install gitignore-cli-tddschn\n```\n\n### [pip](https://pypi.org/project/gitignore-cli-tddschn/)\n```\n$ pip install gitignore-cli-tddschn\n```\n\n\n## Usage\n\nYou can either invoke gitignore CLI with `gi` or `gitignore`.\n\n```\n$ gitignore -h\nusage: gitignore [-h] [-o FILE] [-r] [-l] [-a] [-w] [TEMPLATES ...]\n\ngitignore CLI\n\npositional arguments:\n  TEMPLATES            A positional argument (default: None)\n\noptions:\n  -h, --help           show this help message and exit\n  -o FILE, --out FILE  Output to file, append if exists, if -a or -w is not specified (default: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>)\n  -r, --refresh        Refresh gitignore cache (default: False)\n  -l, --list           Lists available gitignore templates (default: False)\n  -a, --append         Append to the .gitignore of current git repository (default: False)\n  -w, --write          Write to the .gitignore of current git repository (overwrite) (default: False)\n```\n\n## Develop\n```\n$ git clone https://github.com/tddschn/gitignore-cli-tddschn.git\n$ cd gitignore-cli-tddschn\n$ poetry install\n```",
    'author': 'Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tddschn/gitignore-cli-tddschn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
