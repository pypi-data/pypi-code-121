# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chalkit']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['chalkit = chalkit.main:app']}

setup_kwargs = {
    'name': 'chalkit',
    'version': '0.5.0',
    'description': '',
    'long_description': '# chalkit\nChalkit is a CLI tool to save ideas/todos by just opening your terminal.\nThe git repository is automatically committed and pushed.\n\nLets you quickly type your ideas/todos using the terminal and continue on with your work.\n\n![Demo]()\n\n# Initital setup\nRequires a directory containing git repository with a README.md file in it.\nWhen you run chalkit for the first time, it asks for the absolute path for this directory.\n\nThe configuration files are stored as determined by user_config_dir mentioned by [appdirs](https://pypi.org/project/appdirs/)\n\n# How to install\n``` \n$ pip install chalkit\n```\n\n# Commands\n```\n $ eureka    First time setup, edit ur ideas\n```\n\n## Flags\n```\n$ --view      View your ideas in read-only mode\n$ --reset     Reset your configurations\n```\n# Improvements\nFeel free to raise issues, ask for features. Leave a star if helpful.',
    'author': 'Anurag-gg',
    'author_email': 'dsanurag520@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
