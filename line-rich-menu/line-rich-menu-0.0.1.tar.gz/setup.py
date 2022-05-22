# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['line_rich_menu', 'line_rich_menu.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'line-bot-sdk>=2.2.1,<3.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'python-magic>=0.4.25,<0.5.0']

entry_points = \
{'console_scripts': ['line_rich_menu = line_rich_menu.cli.main:main_cli']}

setup_kwargs = {
    'name': 'line-rich-menu',
    'version': '0.0.1',
    'description': 'Rich Menu CLI for Line Bot',
    'long_description': None,
    'author': 'Nuttapat Koonarangsri',
    'author_email': 'webmaster@hackinteach.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
