# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chips', 'chips.commands', 'chips.common', 'chips.services']

package_data = \
{'': ['*']}

install_requires = \
['ast2json>=0.3,<0.4',
 'colorama>=0.4.4,<0.5.0',
 'gitignore-parser>=0.0.8,<0.0.9',
 'prettytable>=3.3.0,<4.0.0']

setup_kwargs = {
    'name': 'python-chips',
    'version': '1.0.12',
    'description': 'A tool that inserts "chips" to your code, detecting unused fragments. Might be used for developing, refactoring and manual testing purposes',
    'long_description': '# 👾 Chips\n\nChips is a tool that inserts "chips" to your code, detecting unused fragments. Then shows unused functions in a pretty table. Might be used for developing, refactoring and manual testing purposes\n\nVisit [chips git](https://github.com/kovalruss/chips) to see the insights..\n\n## Installation\n\n**Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Chips**\n\n```bash\npip install python-chips\n```\n\n**Setup Chips**\n\nBy default chips auto setups everything for you. If you are running into setup problems, use args below.\n1) `-v --venv <on/off>` Determine whether you are using virtualenv or not. If set to `on` Chips will search for a virtualenv on a root path. Defaults to `on`. **Note:** if you are not using virtualenv, you should run commands below with `python -m chips` instead of `$chips` \n2) `-p --path <YOUR_VIRTUALENV_PATH>` Specify virtualenv path if venv not found\n\n```bash\npython -m chips -s\n```\n**Open a new tab in terminal or run** ``source <YOUR_VIRTUALENV_PATH>/bin/activate``\n\n## Usage\n\n1) Add chips to your project (-a --add)\n\n```bash\n$chips -a\n```\n2) Use your code (trigger functions in a way: make api requests, click website, etc..)\n\n3) See the auto generated results at .chipping_results/results.py in a pretty table\n\n![_pretty_table.png](https://raw.githubusercontent.com/kovalruss/chips/master/README_IMGS/_pretty_table.png)\n\n4) Remove chips (-r --remove)\n```bash\n$chips -r\n```\n\n## Ignore particular dirs and files\nTo exclude particular dirs and files from chipping (f.e. tests and manage.py in Django) \nChips generate a .chipsignore file, based on your .gitignore. Syntax is the same.\n\nThere\'s a basic excludes list in .chipsignore. You can modify it any time you want.\n\n![_chipsignore.png](https://raw.githubusercontent.com/kovalruss/chips/master/README_IMGS/_chipsignore.png)\n\n## Chipping path\nBasically Chips are performing on a root path of your project. You can specify a folder or file **local path**, where you want Chips to perform (add or remove). Use -p --path arg.\n```bash\n$chips -a -p <DESIRED PATH>\n```\n\n## Bad performance\nIf you struggle from a bad performance after chipping, use --auto off to turn off auto generated results\n```bash\n$chips -a --auto off\n```\n\nThen you\'ll need to generate results manually (-rs --results)\n```bash\n$chips -rs\n```\n\n## Chips logging\nChoose logging type. Can be applied to remove and add (-rt --result_type)\n1) list_files (default for add) - list all affected files, \n2) count_files (default for remove) - print number of files affected,\n3) blind - no output\n```bash\n$chips -a -rt count_files\n```\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\n[git link](https://github.com/kovalruss/chips)',
    'author': 'Ruslan Kovalchuk',
    'author_email': 'russkovalchuk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
