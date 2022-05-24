# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['domjudge_tool_cli',
 'domjudge_tool_cli.commands',
 'domjudge_tool_cli.commands.emails',
 'domjudge_tool_cli.commands.general',
 'domjudge_tool_cli.commands.problems',
 'domjudge_tool_cli.commands.scoreboard',
 'domjudge_tool_cli.commands.submissions',
 'domjudge_tool_cli.commands.users',
 'domjudge_tool_cli.models',
 'domjudge_tool_cli.services',
 'domjudge_tool_cli.services.v4',
 'domjudge_tool_cli.utils',
 'domjudge_tool_cli.utils.email']

package_data = \
{'': ['*'], 'domjudge_tool_cli': ['templates/csv/*', 'templates/email/*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'httpx>=0.19.0,<0.20.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pydantic[email,dotenv]>=1.8.2,<2.0.0',
 'tablib[all]>=3.0.0,<4.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['domjudge-tool-cli = domjudge_tool_cli:app']}

setup_kwargs = {
    'name': 'domjudge-tool-cli',
    'version': '0.1.1',
    'description': 'DomJudge dom server cli tool.',
    'long_description': None,
    'author': 'Jason Xie',
    'author_email': 'x5758x@gmail.com',
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
